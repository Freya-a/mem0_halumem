import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name('medium_full_evaluation.py')
if MODULE_PATH.exists():
    spec = importlib.util.spec_from_file_location('medium_full_evaluation', MODULE_PATH)
    evaluation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluation)
else:
    evaluation = None


class EvaluationPreparationTests(unittest.TestCase):
    def test_evaluation_bridge_exists(self):
        self.assertIsNotNone(evaluation)

    def fixture(self, root):
        user = {'uuid': 'u1', 'sessions': [{'dialogue': [{'role': 'user', 'content': 'hello', 'timestamp': 't'}],
            'memory_points': [{'memory_content': 'fact', 'is_update': 'True', 'original_memories': ['old']}],
            'questions': [{'question': 'what?', 'answer': 'fact'}]}]}
        source = root / 'dataset.jsonl'
        source.write_text(json.dumps(user) + '\n')
        session = copy.deepcopy(user['sessions'][0])
        session['memory_points'][0]['memories_from_system'] = ['t: fact']
        session['questions'][0].update(system_response='fact', context='context', search_duration_ms=1, response_duration_ms=1)
        session['mem0_add_result'] = {'results': [{'id': 'x', 'memory': 'fact', 'event': 'ADD'}]}
        session['extracted_memories'] = ['fact']
        session['add_dialogue_duration_ms'] = 1
        run = root / 'run'
        run.mkdir()
        (run / 'status.json').write_text(json.dumps({'status': 'completed', 'users': 1, 'qa': True}))
        qa_settings = {'OPENAI_MODEL': 'qwen-plus-2025-12-01',
                       'OPENAI_BASE_URL': 'https://ws-test.cn-beijing.maas.aliyuncs.com/compatible-mode/v1',
                       'OPENAI_TEMPERATURE': '0', 'OPENAI_MAX_TOKENS': '16384', 'OPENAI_TIMEOUT': '180',
                       'RETRY_TIMES': '3', 'WAIT_TIME_LOWER': '10', 'WAIT_TIME_UPPER': '30'}
        (run / 'run.json').write_text(json.dumps({'with_qa': True, 'dataset_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                                                 'profile_sha256': hashlib.sha256(evaluation.baseline.PROFILE.read_bytes()).hexdigest(),
                                                 'qa_settings': qa_settings}))
        (run / 'memzero_eval_results.jsonl').write_text(json.dumps({'uuid': 'u1', 'user_name': 'u1', 'sessions': [session]}) + '\n')
        user_dir = run / 'users/u1/sessions'
        user_dir.mkdir(parents=True)
        (user_dir / '000001.json').write_text(json.dumps(session))
        return run, source

    @unittest.skipIf(evaluation is None, 'bridge not implemented')
    def test_complete_run_is_packaged_in_official_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); run, source = self.fixture(root)
            target = root / 'bundle'
            summary = evaluation.prepare_bundle(run, target, source)
            expected = target / 'results/memzero-full/memzero_eval_results.jsonl'
            self.assertTrue(expected.exists())
            self.assertEqual((summary['users'], summary['sessions'], summary['questions'], summary['updates']), (1, 1, 1, 1))
            with self.assertRaises(FileExistsError): evaluation.prepare_bundle(run, target, source)

    @unittest.skipIf(evaluation is None, 'bridge not implemented')
    def test_missing_qa_is_rejected_without_creating_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); run, source = self.fixture(root)
            input_file = run / 'memzero_eval_results.jsonl'
            user = json.loads(input_file.read_text()); del user['sessions'][0]['questions'][0]['system_response']
            input_file.write_text(json.dumps(user) + '\n')
            with self.assertRaisesRegex(ValueError, 'answer'):
                evaluation.prepare_bundle(run, root / 'bundle', source)
            self.assertFalse((root / 'bundle').exists())

    @unittest.skipIf(evaluation is None, 'bridge not implemented')
    def test_altered_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); run, source = self.fixture(root)
            input_file = run / 'memzero_eval_results.jsonl'
            user = json.loads(input_file.read_text()); user['sessions'][0]['dialogue'][0]['content'] = 'changed'
            input_file.write_text(json.dumps(user) + '\n')
            with self.assertRaisesRegex(ValueError, 'dialogue'):
                evaluation.prepare_bundle(run, root / 'bundle', source)

    @unittest.skipIf(evaluation is None, 'bridge not implemented')
    def test_official_scores_map_to_requested_metrics(self):
        score = {'memory_integrity': {'recall(all)': .1, 'recall(valid)': .2, 'weighted_recall(all)': .3, 'weighted_recall(valid)': .4},
                 'memory_accuracy': {'target_accuracy(all)': .5, 'target_accuracy(valid)': .6, 'weighted_accuracy(all)': .7,
                    'weighted_accuracy(valid)': .8, 'interference_accuracy(all)': .9, 'interference_accuracy(valid)': 1.0},
                 'memory_extraction_f1': .11,
                 'memory_update': {f'{name}_update_memory_ratio({scope})': .21 for name in ('correct','hallucination','omission') for scope in ('all','valid')},
                 'question_answering': {f'{name}_qa_ratio({scope})': .31 for name in ('correct','hallucination','omission') for scope in ('all','valid')}}
        rows = evaluation.metric_rows(score)
        mapped = {(r['stage'], r['metric']): r for r in rows}
        self.assertEqual(mapped['memory_extraction','FMR']['all'], .9)
        self.assertEqual(mapped['memory_extraction','F1']['all'], .11)
        self.assertIsNone(mapped['memory_extraction','F1']['valid'])
        self.assertEqual(mapped['question_answering','O']['valid'], .31)
        self.assertEqual(len(rows), 12)

    @unittest.skipIf(evaluation is None, 'bridge not implemented')
    def test_scoring_rejects_different_workspace_before_any_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); run, source = self.fixture(root)
            target = root / 'bundle'
            evaluation.prepare_bundle(run, target, source)
            settings = {'DASHSCOPE_API_KEY': 'dummy', 'DASHSCOPE_WORKSPACE_ID': 'ws-other', 'EMBEDDING_API_KEY': 'dummy'}
            with patch.object(evaluation.subprocess, 'run', side_effect=AssertionError('scorer must not start')):
                with self.assertRaisesRegex(ValueError, 'QA'):
                    evaluation.score_bundle(target, settings)
            self.assertFalse((target / 'score_config.json').exists())

    @unittest.skipIf(evaluation is None, 'bridge not implemented')
    def test_real_official_scorer_and_metric_export_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); run, source = self.fixture(root)
            user = json.loads(source.read_text())
            session = user['sessions'][0]
            session['memory_points'] = [
                {'memory_content': typ, 'memory_type': typ, 'memory_source': 'primary', 'importance': 1,
                 'is_update': 'False', 'original_memories': []}
                for typ in ('Event Memory', 'Persona Memory', 'Relationship Memory')]
            session['memory_points'].append({'memory_content': 'decoy', 'memory_type': 'Event Memory',
                'memory_source': 'interference', 'importance': 1, 'is_update': 'False', 'original_memories': []})
            session['memory_points'].append({'memory_content': 'updated', 'memory_type': 'Event Memory',
                'memory_source': 'primary', 'importance': 1, 'is_update': 'True', 'original_memories': ['old']})
            session['questions'][0]['evidence'] = [{'memory_content': 'fact'}]
            source.write_text(json.dumps(user) + '\n')
            record = copy.deepcopy(session)
            record['memory_points'][-1]['memories_from_system'] = ['t: updated']
            record['questions'][0].update(system_response='fact', context='context', search_duration_ms=1, response_duration_ms=1)
            record['mem0_add_result'] = {'results': [{'id': 'x', 'memory': 'fact', 'event': 'ADD'}]}
            record['extracted_memories'] = ['fact']
            record['add_dialogue_duration_ms'] = 1
            run_config = json.loads((run / 'run.json').read_text())
            run_config['dataset_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
            (run / 'run.json').write_text(json.dumps(run_config))
            (run / 'memzero_eval_results.jsonl').write_text(json.dumps({'uuid': 'u1', 'user_name': 'u1', 'sessions': [record]}) + '\n')
            (run / 'users/u1/sessions/000001.json').write_text(json.dumps(record))
            target = root / 'bundle'
            evaluation.prepare_bundle(run, target, source)
            fake = root / 'fake'; fake.mkdir()
            (fake / 'sitecustomize.py').write_text(
                "import socket,sys,types\n"
                "def deny(*a,**k): raise RuntimeError('network disabled')\n"
                "socket.socket.connect=deny\n"
                "socket.getaddrinfo=deny\n"
                "m=types.ModuleType('llms')\n"
                "def respond(prompt): return {'score':'2','accuracy_score':'2','is_included_in_golden_memories':'true','evaluation_result':'Correct'}\n"
                "m.llm_request_for_json=respond\n"
                "sys.modules['llms']=m\n")
            settings = {'DASHSCOPE_API_KEY': 'dummy', 'DASHSCOPE_WORKSPACE_ID': 'ws-test', 'EMBEDDING_API_KEY': 'dummy'}
            with patch.dict(os.environ, {'PYTHONPATH': str(fake)}, clear=False):
                evaluation.score_bundle(target, settings)
            result = json.loads((target / 'results/memzero-full/memzero_eval_stat_result.json').read_text())
            self.assertEqual(result['overall_score']['memory_extraction_f1'], 1.0)
            self.assertEqual(result['overall_score']['question_answering']['correct_qa_ratio(all)'], 1.0)
            self.assertEqual(len((target / 'metrics.csv').read_text().splitlines()), 13)
            self.assertEqual(json.loads((target / 'score_config.json').read_text())['judge']['OPENAI_MODEL'], 'qwen-plus-2025-12-01')


if __name__ == '__main__': unittest.main()
