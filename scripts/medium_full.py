#!/usr/bin/env python3
"""Run the full Medium dataset with the local, unmodified Mem0 implementation."""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import re
import shlex
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'config/medium_full_qwen_plus_20251201.json'


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def load_environment(path):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ValueError('Environment file does not exist')
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        line = line.strip().removeprefix('export ')
        if not line or line.startswith('#'):
            continue
        name, sep, raw = line.partition('=')
        name = name.strip()
        if not sep or not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', name):
            raise ValueError(f'Invalid environment assignment at line {number}')
        values = shlex.split(raw, comments=True)
        if len(values) > 1:
            raise ValueError(f'Quote environment value at line {number}')
        os.environ[name] = values[0] if values else ''
    # Do this after loading the file; the native adapter checks this variable twice.
    os.environ.pop('OPENROUTER_API_KEY', None)
    for key in ('DASHSCOPE_API_KEY', 'DASHSCOPE_WORKSPACE_ID', 'EMBEDDING_API_KEY'):
        if not os.environ.get(key, '').strip():
            raise ValueError(f'Missing {key}')
    workspace = os.environ['DASHSCOPE_WORKSPACE_ID']
    if not re.fullmatch(r'(?:llm|ws)-[a-zA-Z0-9-]+', workspace):
        raise ValueError('DASHSCOPE_WORKSPACE_ID must be a Beijing workspace ID such as ws-... or llm-...')
    return {key: os.environ[key] for key in ('DASHSCOPE_API_KEY', 'DASHSCOPE_WORKSPACE_ID', 'EMBEDDING_API_KEY')}


def make_memory_config(settings, user_dir):
    profile = read_json(PROFILE)
    llm = copy.deepcopy(profile['llm'])
    llm['config']['openai_base_url'] = llm['config']['openai_base_url'].replace(
        '{DASHSCOPE_WORKSPACE_ID}', settings['DASHSCOPE_WORKSPACE_ID'])
    llm['config']['api_key'] = settings['DASHSCOPE_API_KEY']
    embedder = copy.deepcopy(profile['embedder'])
    embedder['config']['api_key'] = settings['EMBEDDING_API_KEY']
    return {'version': 'v1.1', 'llm': llm, 'embedder': embedder,
            'vector_store': {'provider': 'qdrant', 'config': {'collection_name': 'medium_full',
                'path': str(user_dir / 'qdrant'), 'on_disk': True, 'embedding_model_dims': 1024}},
            'history_db_path': str(user_dir / 'history.db')}


class ErrorCapture(logging.Handler):
    def __init__(self):
        super().__init__(logging.ERROR)
        self.errors = []

    def emit(self, record):
        try:
            message = record.getMessage()
            for name in ('DASHSCOPE_API_KEY', 'EMBEDDING_API_KEY', 'OPENAI_API_KEY', 'OPENROUTER_API_KEY'):
                secret = os.environ.get(name)
                if secret:
                    message = message.replace(secret, '<redacted>')
            message = re.sub(r'\bsk-[A-Za-z0-9_-]+', '<redacted>', message)
            self.errors.append({'logger': record.name, 'message': message})
        except Exception:
            self.errors.append({'logger': record.name, 'message': 'Unable to format original log message'})


def search(memory, query, uid, limit):
    start = time.monotonic()
    results = memory.search(query, user_id=uid, limit=limit)['results']
    formatted = [f"{item.get('created_at', '')}: {item['memory']}" for item in results]
    return formatted, (time.monotonic() - start) * 1000


def process_user(memory, user, user_dir, qa=None):
    user_dir = Path(user_dir)
    session_dir = user_dir / 'sessions'
    session_dir.mkdir(parents=True, exist_ok=True)
    marker = user_dir / 'incomplete.json'
    if marker.exists():
        raise RuntimeError(f'An incomplete session exists in {user_dir}; inspect it before any rerun')
    uid = user['uuid']
    for index, session in enumerate(user['sessions'], 1):
        output = session_dir / f'{index:06d}.json'
        if output.exists():
            continue
        atomic_json(marker, {'session': index})
        messages = [{'role': item['role'], 'content': item['content']} for item in session['dialogue']]
        capture = ErrorCapture()
        logging.getLogger('mem0').addHandler(capture)
        try:
            start = time.monotonic()
            result = memory.add(messages, user_id=uid)
            duration = (time.monotonic() - start) * 1000
        finally:
            logging.getLogger('mem0').removeHandler(capture)
            if capture.errors:
                atomic_json(user_dir / 'native_errors' / f'{index:06d}.json', capture.errors)
                print(f'{uid} session {index}: Mem0 logged {len(capture.errors)} error(s); see native_errors/', flush=True)
        record = copy.deepcopy(session)
        record['add_dialogue_duration_ms'] = duration
        record['mem0_add_result'] = result
        record['mem0_errors'] = capture.errors
        record['extracted_memories'] = [item['memory'] for item in result['results']]
        for point in record.get('memory_points', []):
            if str(point.get('is_update')) == 'False' or not point.get('original_memories'):
                continue
            point['memories_from_system'], _ = search(memory, point['memory_content'], uid, 10)
        if qa:
            for question in record.get('questions', []):
                memories, duration = search(memory, question['question'], uid, 20)
                context = f'Memories for user {uid}:\n\n    {json.dumps(memories, indent=4)}\n'
                start = time.monotonic()
                answer = qa(context, question['question'])
                if not isinstance(answer, str) or not answer.strip():
                    raise ValueError('QA answer was empty; session remains incomplete')
                question['system_response'] = answer
                question['context'] = context
                question['search_duration_ms'] = duration
                question['response_duration_ms'] = (time.monotonic() - start) * 1000
        atomic_json(output, record)
        marker.unlink()
        print(f'{uid}: completed session {index}/{len(user["sessions"])}', flush=True)


def close_memory(memory):
    memory.vector_store.client.close()
    memory._telemetry_vector_store.client.close()
    memory.db.connection.close()
    memory.llm.client.close()
    memory.embedding_model.client.close()


def export_native_results(run, users):
    output = run / 'mem0_native_results.jsonl'
    tmp = output.with_suffix('.jsonl.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        for user in users:
            for index in range(1, len(user['sessions']) + 1):
                session = read_json(run / 'users' / user['uuid'] / 'sessions' / f'{index:06d}.json')
                row = {'user_id': user['uuid'], 'session_index': index, 'result': session['mem0_add_result']}
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, output)


def configure_qa(settings):
    profile = read_json(PROFILE)
    llm = profile['llm']['config']
    config = profile['qa_and_judge']
    values = {'OPENAI_API_KEY': settings['DASHSCOPE_API_KEY'],
              'OPENAI_BASE_URL': llm['openai_base_url'].replace('{DASHSCOPE_WORKSPACE_ID}', settings['DASHSCOPE_WORKSPACE_ID']),
              'OPENAI_MODEL': llm['model'], 'OPENAI_TEMPERATURE': str(config['temperature']),
              'OPENAI_MAX_TOKENS': str(config['max_tokens']), 'OPENAI_TIMEOUT': str(config['timeout_seconds']),
              'RETRY_TIMES': str(config['retry_times']), 'WAIT_TIME_LOWER': str(config['wait_time_lower']),
              'WAIT_TIME_UPPER': str(config['wait_time_upper'])}
    os.environ.update(values)


def get_qa(settings):
    configure_qa(settings)
    sys.path.insert(0, str(ROOT / 'HaluMem/eval'))
    from llms import llm_request
    from prompts import PROMPT_MEMZERO
    return lambda context, question: llm_request(PROMPT_MEMZERO.format(context=context, question=question))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', required=True)
    parser.add_argument('--run-id')
    parser.add_argument('--check', action='store_true', help='validate configuration and dataset without running the experiment')
    parser.add_argument('--resume', action='store_true')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--with-qa', dest='with_qa', action='store_true', default=True)
    modes.add_argument('--without-qa', dest='with_qa', action='store_false', help='write-only run; unsuitable for full QA scoring')
    args = parser.parse_args()
    if not args.check and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}', args.run_id or ''):
        raise ValueError('Invalid run ID')
    settings = load_environment(args.env_file)
    qa = get_qa(settings) if args.with_qa else None
    # The existing QA module also loads dotenv, which may reintroduce OpenRouter.
    os.environ.pop('OPENROUTER_API_KEY', None)
    profile = read_json(PROFILE)
    dataset = ROOT / profile['dataset']
    dataset_hash = digest(dataset)
    if dataset_hash != profile['dataset_sha256']:
        raise ValueError('Medium dataset SHA-256 does not match the pinned dataset')
    if args.check:
        with dataset.open(encoding='utf-8') as f:
            users = [json.loads(line) for line in f if line.strip()]
        config = make_memory_config(settings, Path('/offline-check'))
        print(f"Dataset: {len(users)} users, {sum(len(u['sessions']) for u in users)} sessions")
        print(f"Mem0 LLM: {config['llm']['config']['model']} at {config['llm']['config']['openai_base_url']}")
        if args.with_qa:
            print(f"QA and judge LLM: {os.environ['OPENAI_MODEL']} at {os.environ['OPENAI_BASE_URL']}")
        print('OpenRouter: unset; credentials: present; no model request was made')
        print(f"QA: {'enabled' if args.with_qa else 'disabled'}; official scoring: separate")
        return
    run = ROOT / 'results/medium_full' / args.run_id
    run.parent.mkdir(parents=True, exist_ok=True)
    run.mkdir(mode=0o700, exist_ok=True)
    with (run / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        record_path = run / 'run.json'
        existing = record_path.exists()
        if existing != args.resume:
            raise ValueError('Existing runs require --resume; new runs must omit it')
        source_files = ['mem0/memory/main.py', 'mem0/configs/prompts.py', 'mem0/llms/openai.py',
                        'mem0/embeddings/openai.py', 'mem0/vector_stores/qdrant.py']
        record = {'dataset_sha256': dataset_hash, 'profile_sha256': digest(PROFILE),
                  'runner_sha256': digest(Path(__file__)), 'with_qa': args.with_qa,
                  'workspace': settings['DASHSCOPE_WORKSPACE_ID'], 'mem0ai_version': '0.1.118',
                  'native_source_sha256': {name: digest(ROOT / 'mem0_v0.1.118' / name) for name in source_files}}
        if args.with_qa:
            record['qa_settings'] = {key: os.environ.get(key) for key in (
                'OPENAI_BASE_URL', 'OPENAI_MODEL', 'OPENAI_MAX_TOKENS', 'OPENAI_TEMPERATURE',
                'OPENAI_TIMEOUT', 'RETRY_TIMES', 'WAIT_TIME_LOWER', 'WAIT_TIME_UPPER')}
            record['qa_source_sha256'] = {name: digest(ROOT / 'HaluMem/eval' / name)
                                           for name in ('llms.py', 'prompts.py')}
        if existing and read_json(record_path) != record:
            raise ValueError('Run configuration changed; choose a new run ID')
        if any((run / 'users').glob('*/incomplete.json')):
            raise RuntimeError('An incomplete session exists; inspect it before any rerun')
        if not existing:
            atomic_json(record_path, record)
        os.environ['MEM0_DIR'] = str(run / 'mem0_runtime')
        os.environ['MEM0_TELEMETRY'] = 'False'
        sys.path.insert(0, str(ROOT / 'mem0_v0.1.118'))
        import mem0
        if Path(mem0.__file__).resolve() != ROOT / 'mem0_v0.1.118/mem0/__init__.py' or importlib.metadata.version('mem0ai') != '0.1.118':
            raise RuntimeError('Expected the local Mem0 v0.1.118 installation')
        users = []
        with dataset.open(encoding='utf-8') as f:
            for line in f:
                if line.strip(): users.append(json.loads(line))
        if len({u['uuid'] for u in users}) != len(users):
            raise ValueError('Dataset contains duplicate user IDs')
        for user in users:
            uid = user['uuid']
            if not re.fullmatch(r'[A-Za-z0-9-]+', uid):
                raise ValueError('Unsafe user ID in dataset')
            user_dir = run / 'users' / uid
            user_dir.mkdir(parents=True, exist_ok=True)
            memory = mem0.Memory.from_config(make_memory_config(settings, user_dir))
            try:
                process_user(memory, user, user_dir, qa)
            finally:
                close_memory(memory)
        output = run / 'memzero_eval_results.jsonl'
        tmp = output.with_suffix('.jsonl.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            for user in users:
                sessions = [read_json(run / 'users' / user['uuid'] / 'sessions' / f'{i:06d}.json')
                            for i in range(1, len(user['sessions']) + 1)]
                f.write(json.dumps({'uuid': user['uuid'], 'user_name': user['uuid'], 'sessions': sessions}, ensure_ascii=False) + '\n')
        os.replace(tmp, output)
        export_native_results(run, users)
        atomic_json(run / 'status.json', {'status': 'completed', 'users': len(users), 'qa': args.with_qa,
                                          'official_scoring': 'not_run'})
        print(f'Completed {len(users)} users. Output: {output}', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        message = str(exc)
        for name in ('DASHSCOPE_API_KEY', 'EMBEDDING_API_KEY', 'OPENAI_API_KEY', 'OPENROUTER_API_KEY'):
            secret = os.environ.get(name)
            if secret: message = message.replace(secret, '<redacted>')
        print(f'Run stopped: {message}', file=sys.stderr, flush=True)
        sys.exit(1)
