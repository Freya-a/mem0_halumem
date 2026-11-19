"""One-shot scoped experiment; never writes Mem0 and reserves every call on disk."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
sys.path.insert(0, str(PROJECT/'variants/evidence_temporal_judge'))
sys.path.insert(0, str(PROJECT/'variants/dnd_mem0_splitter'))
import judge
from real_backend import OpenAICompatibleBackend, load_model_settings

MANIFEST = PROJECT/'results/medium_dev/scoring_review_and_five_case_plan_20261029_v1/five_case_manifest.json'
DATASET = PROJECT/'dataset/HaluMem-Medium/HaluMem-Medium.jsonl'
REVIEW = PROJECT/'diagnosis/medium_dev/human_review.csv'
SPECS = [
    {'key':'target_10', 'name':'promotion', 'row':14, 'old_session':1, 'old_message':2,
     'old_quote':'I work at Historical Productions Ltd. as a Director.', 'new_indices':[0], 'review_row':10},
    {'key':'A', 'name':'skydiving', 'row':1, 'old_session':2, 'old_message':6,
     'old_quote':'I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.', 'new_indices':[0,2,8], 'review_row':8},
    {'key':'C', 'name':'career_history', 'row':17, 'old_session':1, 'old_message':2,
     'old_quote':'I work at Blockchain Tech as a senior developer.', 'new_indices':[0], 'review_row':24},
]

class BudgetExhausted(Exception): pass
class CandidateStageDeferred(Exception): pass
class ModelCallFailed(Exception): pass


def stamp(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path, value):
    path = Path(path)
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def prepare_cases():
    manifest = json.loads(MANIFEST.read_text())
    lines = DATASET.read_text(encoding='utf-8').splitlines()
    out = []
    for spec in SPECS:
        meta = next(x for x in manifest['cases'] if x['case'] == spec['key'])
        before, source = Path(meta['before_path']), Path(meta['input_path'])
        if digest(before) != meta['before_sha256'] or digest(source) != meta['input_sha256']:
            raise ValueError('source hash differs from frozen manifest: '+spec['name'])
        record = json.loads(lines[spec['row']-1])
        if record['uuid'] != meta['user_uuid']:
            raise ValueError('source user mismatch')
        snapshot = json.loads(before.read_text())
        matches = [x for x in snapshot['api_snapshot']['results'] if x['id']==meta['target_memory_id']]
        if len(matches) != 1 or matches[0]['memory'] != meta['target_memory_text']:
            raise ValueError('snapshot identity mismatch')
        source_data = json.loads(source.read_text())
        if source_data['user_uuid'] != record['uuid'] or source_data['original_session_index_zero_based'] != meta['original_session_index']:
            raise ValueError('session identity mismatch')
        original_dialogue = record['sessions'][meta['original_session_index']]['dialogue']
        for i in spec['new_indices']:
            a,b=source_data['raw_dialogue'][i], original_dialogue[i]
            if any(a.get(k)!=b.get(k) for k in ('role','content','timestamp')) or a['role'] != 'user':
                raise ValueError('source message mismatch')
        old = record['sessions'][spec['old_session']]['dialogue'][spec['old_message']]
        if old['role'] != 'user' or spec['old_quote'] not in old['content']:
            raise ValueError('old context missing')
        new = [{'source_id':f'dialogue-{i}', 'text':source_data['raw_dialogue'][i]['content'],
                'speaker':'user','recorded_at':source_data['raw_dialogue'][i]['timestamp']} for i in spec['new_indices']]
        old_ref = f"dataset line {spec['row']}, /sessions/{spec['old_session']}/dialogue/{spec['old_message']}/content"
        request = {'memory_id': matches[0]['id'], 'memory_text': matches[0]['memory'],
                   'source_context':[{'source_id':'old-context-1','source_ref':old_ref, 'text':spec['old_quote'],
                                      'speaker':'user','recorded_at':old['timestamp']}]}
        provenance = {'case_name':spec['name'], 'user_uuid':record['uuid'],
          'before_file':str(before), 'before_sha256':digest(before),
          'snapshot_pointer':'/api_snapshot/results/'+str(snapshot['api_snapshot']['results'].index(matches[0])),
          'input_file':str(source), 'input_sha256':digest(source),
          'new_evidence_pointers':[f'/raw_dialogue/{i}' for i in spec['new_indices']],
          'dataset_file':str(DATASET), 'dataset_sha256':digest(DATASET), 'old_context_pointer':old_ref,
          'old_quote_character_range':[old['content'].index(spec['old_quote']), old['content'].index(spec['old_quote'])+len(spec['old_quote'])],
          'human_review_file':str(REVIEW), 'human_review_sha256':digest(REVIEW), 'human_review_row_one_based':spec['review_row'],
          'review_scope_note':'用户确认原始事实及范围；本次运行的判断正确性尚未由用户确认'}
        out.append({'name':spec['name'], 'request':request, 'new_evidence':new, 'time_info':None, 'provenance':provenance})
    return out


class RunRecorder:
    def __init__(self, root, maximum=10):
        self.root, self.maximum, self.count = Path(root), maximum, 0
        (self.root/'calls').mkdir(exist_ok=True)
    def event(self, value):
        with (self.root/'call_journal.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(value, ensure_ascii=False)+'\n'); f.flush(); os.fsync(f.fileno())
    def call(self, case, stage, prompt, request, invoke):
        if self.count >= self.maximum: raise BudgetExhausted('global request cap reached')
        self.count += 1
        number = self.count
        folder = self.root/'calls'/f'{number:02d}_{case}_{stage}'
        folder.mkdir(exist_ok=False)
        write_json(folder/'request.json', {'system_prompt':prompt, 'input':request})
        self.event({'number':number,'case':case,'stage':stage,'event':'reserved_before_request','time':stamp()})
        try:
            value, info = invoke(prompt, request)
            if info.get('raw') is not None:
                (folder/'raw_content.txt').write_text(info['raw'],encoding='utf-8')
            write_json(folder/'response_metadata.json', {k:v for k,v in info.items() if k != 'raw'})
            if info.get('error_type'):
                raise ModelCallFailed(info['error_type'])
            write_json(folder/'parsed_response.json', value)
            self.event({'number':number,'event':'returned','time':stamp(),'attempted':info.get('attempted')})
            return value
        except Exception as error:
            self.event({'number':number,'event':'failed','time':stamp(),'error_type':type(error).__name__})
            raise


def network_invoke(settings):
    def invoke(prompt, request):
        backend = None
        try:
            backend = OpenAICompatibleBackend(settings, prompt)
            result = backend(request)
            return result, {'attempted':bool(backend.call_count), 'metadata':backend.response_metadata,
                            'raw':backend.raw_content.replace(settings.api_key,'[REDACTED]') if isinstance(backend.raw_content,str) else None}
        except Exception as exc:
            return None, {'attempted':bool(backend and backend.call_count), 'error_type':type(exc).__name__,
                          'error_code':getattr(exc,'code',None), 'metadata':backend.response_metadata if backend else {},
                          'raw':backend.raw_content.replace(settings.api_key,'[REDACTED]') if backend and isinstance(backend.raw_content,str) else None}
        finally:
            if backend: backend.close()
    return invoke


def main():
    if sys.argv[1:] != ['--execute']:
        print('Pass --execute once to start the authorized model requests.'); return 2
    cases = prepare_cases()
    settings = load_model_settings(PROJECT/'.env.local')
    (HERE/'RUN_STARTED').open('x').write(stamp()+'\n')
    config = {'started_at':stamp(), 'model':settings.model, 'generation_parameters':settings.generation,
              'timeout_seconds':settings.timeout, 'sdk_max_retries':0, 'http_follow_redirects':False,
              'endpoint_host':urlsplit(settings.base_url).hostname, 'settings_sources':settings.provenance,
              'request_limit':10, 'prompt_path':str(judge.V4_PROMPT), 'prompt_sha256':digest(judge.V4_PROMPT),
              'selection':['promotion','skydiving','career_history'],
              'candidate_extraction':'deferred in judge calls to prioritize module-one fact scope'}
    write_json(HERE/'run_config.json',config)
    invoke=network_invoke(settings); recorder=RunRecorder(HERE)
    for c in cases:
        directory=HERE/c['name']; directory.mkdir(exist_ok=False)
        write_json(directory/'source_provenance.json', c['provenance'])
        write_json(directory/'model_input.json', {'split_request':c['request'],'new_evidence':c['new_evidence'],'time_info':c['time_info']})
        try:
            def factory(prompt):
                return lambda request: recorder.call(c['name'], 'split', prompt, request, invoke)
            split=judge.split_with_v4(c['request'],factory)
            write_json(directory/'split_result.json',split)
            c['split']=split['result']
        except Exception as e:
            write_json(directory/'split_error.json', {'error_type':type(e).__name__,'error_code':getattr(e,'code',None)})
    for c in cases:
        if 'split' not in c: continue
        def fact_backend(payload):
            payload=payload.copy(); prompt=payload.pop('prompt')
            return recorder.call(c['name'], 'fact', prompt, payload, invoke)
        def deferred(payload): raise CandidateStageDeferred()
        try:
            result=judge.judge(c['split'], c['request']['source_context'],c['new_evidence'],c['time_info'],fact_backend,deferred)
            write_json(HERE/c['name']/'judge_result.json',result)
        except Exception as e:
            write_json(HERE/c['name']/'judge_error.json', {'error_type':type(e).__name__,'error_code':getattr(e,'code',None)})
    # Candidate extraction is secondary to the requested fact scope. Use only remaining budget.
    for c in cases:
        if 'split' not in c: continue
        target=HERE/c['name']/'candidate_stage.json'
        if recorder.count >= recorder.maximum:
            write_json(target, {'status':'not_run','reason':'request cap reached'}); continue
        payload={'task':'new_candidates','new_evidence':c['new_evidence'], 'time_info':c['time_info'], 'old_facts':c['split']['facts']}
        try:
            response=recorder.call(c['name'],'candidate',judge.CANDIDATE_PROMPT,payload,invoke)
            judge._validate_candidates(response,judge._sources(c['new_evidence']))
            write_json(target,{'status':'ok',**response})
        except Exception as e:
            write_json(target,{'status':'failed','error_type':type(e).__name__})
    events=[json.loads(x) for x in (HERE/'call_journal.jsonl').read_text().splitlines()] if recorder.count else []
    write_json(HERE/'run_summary.json',{'finished_at':stamp(),'reserved_count':recorder.count,
        'request_limit':recorder.maximum,'actual_sdk_attempts':sum(1 for p in (HERE/'calls').glob('*/response_metadata.json') if json.loads(p.read_text()).get('attempted')),
        'ambiguous_attempts':recorder.count-sum(1 for _ in (HERE/'calls').glob('*/response_metadata.json')),
        'failed_journal_events':sum(1 for e in events if e['event']=='failed')})
    return 0

if __name__=='__main__': raise SystemExit(main())
