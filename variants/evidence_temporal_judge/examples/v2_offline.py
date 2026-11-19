"""Handwritten synthetic example: no credentials, network, model, or Mem0."""
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import judge_v2

request = {'memory_id': 'synthetic-m1', 'memory_text': '小李从2020年1月1日起住在北京，喜欢茶。', 'source_context': []}
evidence = [{'source_id': 'synthetic-new1', 'text': '小李2023年1月1日搬到上海，现在住在上海。', 'recorded_at': '2023-03-01'}]
facts = {'facts': [{'fact_index': 1, 'source_memory_id': 'synthetic-m1',
    'raw_subfact': request['memory_text'], 'contextualized_subfact': request['memory_text'],
    'evidence': [{'source_type': 'memory', 'source_id': 'synthetic-m1', 'quote': request['memory_text'], 'supports': '旧记忆原文'}],
    'pending_confirmations': []}]}
impact = {'erase_label': 'Make False', 'applicability': 'involved', 'temporal_relation': 'before_after',
    'temporal_reason': '模拟判断：搬家前后居住状态变化', 'components': [
        {'fragment': '小李从2020年1月1日起住在北京', 'action': 'modify', 'reason': '住址可能发生变化',
         'new_evidence': [{'source_id': 'synthetic-new1', 'quote': '2023年1月1日搬到上海'}]},
        {'fragment': '喜欢茶', 'action': 'protect', 'reason': '新证据未涉及', 'new_evidence': []}]}
day = lambda s: {'value': s, 'precision': 'day'}
time_info = {'facts': {'1': {'start': day('2020-01-01'), 'end': None,
    'basis': {'source_type': 'memory', 'source_id': 'synthetic-m1', 'quote': '2020年1月1日起住在北京'}}},
    'sources': {'synthetic-new1': {'start': day('2023-01-01'), 'end': None, 'kind': 'actual',
        'basis': {'source_id': 'synthetic-new1', 'quote': '2023年1月1日搬到上海'}}},
    'transitions': [{'fact_index': 1, 'source_id': 'synthetic-new1', 'quote': '2023年1月1日搬到上海',
                     'at': day('2023-01-01'), 'kind': 'actual'}]}

result = judge_v2.split_and_judge(request, evidence, time_info,
    lambda prompt: lambda payload: deepcopy(facts),
    lambda payload: deepcopy(impact),
    lambda payload: {'candidates': [{'source_id': 'synthetic-new1', 'quote': '现在住在上海', 'reason': '新的住址候选'}]},
    lambda payload: {'relation': 'contradiction', 'score': 0.93},
    # Handwritten synthetic assessment for this example, not semantic verification.
    time_verifier=lambda payload: {'status': 'supported', 'reason': '合成示例中的手写时间语义判断'})
print(json.dumps(result, ensure_ascii=False, indent=2))
