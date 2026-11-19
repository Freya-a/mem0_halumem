import importlib.util
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location('medium_full', Path(__file__).with_name('medium_full.py'))
runner = importlib.util.module_from_spec(SPEC) if SPEC.loader else None
if runner is not None and Path(SPEC.origin).exists():
    SPEC.loader.exec_module(runner)
else:
    runner = None


class MediumFullTests(unittest.TestCase):
    def test_runner_exists(self):
        self.assertIsNotNone(runner, 'Full Medium runner must exist')

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_env_file_cannot_redirect_model_or_openrouter(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'OPENROUTER_API_KEY': 'inherited'}, clear=True):
            env = Path(tmp) / 'env'
            env.write_text('DASHSCOPE_API_KEY=key\nDASHSCOPE_WORKSPACE_ID=llm-123\nEMBEDDING_API_KEY=embed\nOPENROUTER_API_KEY=fromfile\n')
            settings = runner.load_environment(env)
            config = runner.make_memory_config(settings, Path(tmp))
            self.assertFalse(os.environ.get('OPENROUTER_API_KEY'))
            self.assertEqual(config['llm']['config']['model'], 'qwen-plus-2025-12-01')
            self.assertEqual(config['llm']['config']['api_key'], 'key')
            self.assertEqual(config['llm']['config']['openai_base_url'], 'https://llm-123.cn-beijing.maas.aliyuncs.com/compatible-mode/v1')
            self.assertEqual(config['embedder']['config']['model'], 'text-embedding-v4')
            self.assertEqual(config['embedder']['config']['embedding_dims'], 1024)

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_beijing_workspace_accepts_ws_prefixed_id(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {}, clear=True):
            env = Path(tmp) / 'env'
            env.write_text('DASHSCOPE_API_KEY=key\nDASHSCOPE_WORKSPACE_ID=ws-example123\nEMBEDDING_API_KEY=embed\n')
            settings = runner.load_environment(env)
            config = runner.make_memory_config(settings, Path(tmp))
            self.assertEqual(config['llm']['config']['openai_base_url'],
                             'https://ws-example123.cn-beijing.maas.aliyuncs.com/compatible-mode/v1')

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_qa_and_judge_use_pinned_model_and_same_workspace(self):
        with patch.dict(os.environ, {'OPENAI_MODEL': 'old-model', 'OPENAI_API_KEY': 'wrong'}, clear=True):
            settings = {'DASHSCOPE_API_KEY': 'key', 'DASHSCOPE_WORKSPACE_ID': 'ws-example', 'EMBEDDING_API_KEY': 'embed'}
            runner.configure_qa(settings)
            self.assertEqual(os.environ['OPENAI_MODEL'], 'qwen-plus-2025-12-01')
            self.assertEqual(os.environ['OPENAI_API_KEY'], 'key')
            self.assertEqual(os.environ['OPENAI_BASE_URL'], 'https://ws-example.cn-beijing.maas.aliyuncs.com/compatible-mode/v1')
            self.assertEqual(os.environ['OPENAI_TEMPERATURE'], '0')

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_all_sessions_are_processed_in_dataset_order_and_resume_skips_committed(self):
        class Memory:
            def __init__(self): self.inputs = []
            def add(self, messages, user_id):
                self.inputs.append((messages, user_id))
                return {'results': [{'id': 'native-id', 'memory': messages[0]['content'], 'event': 'ADD'}]}
            def search(self, query, user_id, limit): return {'results': []}
        user = {'uuid': 'u1', 'sessions': [
            {'dialogue': [{'role': 'user', 'content': 'first'}], 'memory_points': []},
            {'dialogue': [{'role': 'user', 'content': 'second'}], 'memory_points': []}]}
        with tempfile.TemporaryDirectory() as tmp:
            memory = Memory()
            runner.process_user(memory, user, Path(tmp))
            runner.process_user(memory, user, Path(tmp))
            self.assertEqual([x[0][0]['content'] for x in memory.inputs], ['first', 'second'])
            self.assertEqual(len(json.loads((Path(tmp) / 'sessions/000002.json').read_text())['extracted_memories']), 1)
            saved = json.loads((Path(tmp) / 'sessions/000001.json').read_text())
            self.assertEqual(saved['mem0_add_result'], {'results': [{'id': 'native-id', 'memory': 'first', 'event': 'ADD'}]})

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_export_keeps_each_unmodified_native_add_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            sessions = run / 'users' / 'u1' / 'sessions'
            sessions.mkdir(parents=True)
            (sessions / '000001.json').write_text(json.dumps({'mem0_add_result': {'results': [{'id': 'x', 'event': 'UPDATE', 'memory': 'new', 'old_memory': 'old'}]}}))
            runner.export_native_results(run, [{'uuid': 'u1', 'sessions': [{}]}])
            rows = [json.loads(line) for line in (run / 'mem0_native_results.jsonl').read_text().splitlines()]
            self.assertEqual(rows, [{'user_id': 'u1', 'session_index': 1, 'result': {'results': [{'id': 'x', 'event': 'UPDATE', 'memory': 'new', 'old_memory': 'old'}]}}])

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_interrupted_session_refuses_to_continue(self):
        class Memory:
            def add(self, messages, user_id): raise RuntimeError('interrupted')
        user = {'uuid': 'u1', 'sessions': [{'dialogue': [], 'memory_points': []}]}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                runner.process_user(Memory(), user, Path(tmp))
            with self.assertRaisesRegex(RuntimeError, 'incomplete'):
                runner.process_user(Memory(), user, Path(tmp))

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_native_logged_error_does_not_discard_return_or_stop_following_session(self):
        class Memory:
            def __init__(self): self.calls = 0
            def add(self, messages, user_id):
                self.calls += 1
                if self.calls == 1:
                    logging.getLogger('mem0.memory.main').error('Native action error; key=%s', os.environ['DASHSCOPE_API_KEY'])
                return {'results': [{'id': str(self.calls), 'memory': 'saved', 'event': 'ADD'}]}
            def search(self, query, user_id, limit): return {'results': []}
        user = {'uuid': 'u1', 'sessions': [{'dialogue': [], 'memory_points': []}, {'dialogue': [], 'memory_points': []}]}
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'DASHSCOPE_API_KEY': 'private-secret'}, clear=False):
            memory = Memory()
            runner.process_user(memory, user, Path(tmp))
            self.assertEqual(memory.calls, 2)
            saved = json.loads((Path(tmp) / 'sessions/000001.json').read_text())
            self.assertEqual(saved['mem0_add_result']['results'][0]['id'], '1')
            errors = saved['mem0_errors']
            self.assertIn('Native action error', errors[0]['message'])
            self.assertNotIn('private-secret', json.dumps(errors))
            self.assertFalse((Path(tmp) / 'incomplete.json').exists())
            self.assertTrue((Path(tmp) / 'sessions/000002.json').exists())

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_qa_option_records_retrieval_and_answer_at_each_session(self):
        class Memory:
            def add(self, messages, user_id): return {'results': []}
            def search(self, query, user_id, limit):
                return {'results': [{'created_at': 'date', 'memory': 'remembered'}]}
        user = {'uuid': 'u1', 'sessions': [{'dialogue': [], 'memory_points': [],
                                            'questions': [{'question': 'what?'}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            runner.process_user(Memory(), user, Path(tmp), lambda context, question: 'answer')
            saved = json.loads((Path(tmp) / 'sessions/000001.json').read_text())
            self.assertEqual(saved['questions'][0]['system_response'], 'answer')
            self.assertIn('remembered', saved['questions'][0]['context'])

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_empty_qa_answer_keeps_session_incomplete(self):
        class Memory:
            def add(self, messages, user_id): return {'results': []}
            def search(self, query, user_id, limit): return {'results': []}
        user = {'uuid': 'u1', 'sessions': [{'dialogue': [], 'memory_points': [], 'questions': [{'question': 'what?'}]}]}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'QA answer'):
                runner.process_user(Memory(), user, Path(tmp), lambda context, question: '')
            self.assertTrue((Path(tmp) / 'incomplete.json').exists())

    @unittest.skipIf(runner is None, 'runner not implemented')
    def test_check_mode_reads_full_dataset_without_starting_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / 'env'
            env.write_text('DASHSCOPE_API_KEY=dummy\nDASHSCOPE_WORKSPACE_ID=llm-test\nEMBEDDING_API_KEY=other\n')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('medium_full.py')),
                                     '--env-file', str(env), '--check'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('20 users', result.stdout)
            self.assertIn('1387 sessions', result.stdout)
            self.assertIn('qwen-plus-2025-12-01', result.stdout)
            self.assertIn('QA: enabled', result.stdout)
            self.assertNotIn('dummy', result.stdout)


if __name__ == '__main__': unittest.main()
