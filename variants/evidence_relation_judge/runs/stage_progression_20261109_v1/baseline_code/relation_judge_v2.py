"""Controlled v2: candidate relations, preserving v1 provenance checks and six labels."""
from copy import deepcopy
import json

import relation_judge as v1

LABELS = v1.LABELS
SYSTEM = v1.SYSTEM + '''
补充约束：candidate_impact_fragment 只能从旧事实的 memory 引文中原样复制连续片段；new_quote 只能复制新证据来源中的原文。二者不得互换，即使新证据更适合描述变化也不能把它填入旧片段。不要改大小写或标点；无法定位时留空。
比较同一对象的具体属性与条件，区分同一事实中的不同属性。优先选择足以完整表达受影响属性且有依据的旧文局部片段，保留理解所需的对象、条件和否定；不要为了缩短而破坏语义。如果只能选整个旧事实，请在 reason 解释为何无法缩小，或提出具体待确认问题；片段仍只是候选，不表示整句都应修改。
活动必须比较实际对象和条件：模拟活动的体验不等于真实活动，也不自动推翻对真实活动的态度或风险判断；证据不能确定时提出针对差异的确认问题。使用全部给定证据，已明确的事实不要当作未知反复询问；不要把过去来源的当时状态擅自当成现在状态。理由准确概括原文，不引入新事件、关系或未证明的时间。提问只能针对材料实际留下的关键不确定性，不能包含无依据的前提。'''


def locate_fragment(memory, raw, quotes):
    """Locate case-only correction uniquely across memory and within fact provenance.

    Offsets are Python Unicode character positions, end exclusive. Casefold is
    used only on same-length substrings; whitespace, punctuation and Unicode
    normalization are never changed. All overlapping positions are counted.
    """
    if not isinstance(raw, str):
        raise ValueError('candidate fragment must be a string')
    result = {'raw':raw, 'located':None, 'method':None, 'start':None, 'end':None}
    if not raw:
        result.update(located='', method='empty')
        return result
    locations = [i for i in range(len(memory)-len(raw)+1) if memory[i:i+len(raw)].casefold() == raw.casefold()]
    if not locations:
        result['method'] = 'not_found'
        return result
    def belongs(start, size):
        for quote in quotes:
            pos = memory.find(quote)
            while pos != -1:
                if pos <= start and start+size <= pos+len(quote):
                    return True
                pos = memory.find(quote, pos+1)
        return False
    exact = [i for i in locations if memory[i:i+len(raw)] == raw and belongs(i,len(raw))]
    if exact:
        result.update(located=raw, method='exact')
        if len(exact) == 1:
            result.update(start=exact[0], end=exact[0]+len(raw))
        return result
    if len(locations) != 1:
        result['method'] = 'ambiguous_casefold'
        return result
    start = locations[0]
    if not belongs(start,len(raw)):
        result['method'] = 'outside_fact_evidence'
        return result
    result.update(located=memory[start:start+len(raw)], method='unique_casefold', start=start, end=start+len(raw))
    return result


def judge(data, backend):
    """Backend returns raw JSON; preserve raw and located candidates, no retry."""
    result = {'status':'ok', 'results':[], 'errors':[]}
    try:
        new_map = v1.validate_request(data)
    except Exception as e:
        result.update(status='input_error', errors=[{'stage':'input','type':type(e).__name__,'message':str(e)}])
        return result
    split = data['split_result']
    for fact in split['facts']:
        row = {'memory_id':split['memory_id'], 'fact_index':fact['fact_index'], 'old_subfact':fact['raw_subfact'], 'status':'error', 'raw_output':None, 'candidate':None, 'located_candidate':None, 'fragment_match':None, 'validation':{'passed':False, 'semantic_correctness':'not_checked'}, 'errors':[]}
        payload = {'memory_id':split['memory_id'], 'memory_text':split['memory_text'], 'fact':deepcopy(fact), 'source_context':deepcopy(data.get('source_context', [])), 'new_evidence':deepcopy(data['new_evidence']), 'time_info':deepcopy(data.get('time_info'))}
        stage = 'model'
        try:
            row['raw_output'] = backend(payload)
            stage = 'parse'
            row['candidate'] = json.loads(row['raw_output'])
            stage = 'validation'
            c = deepcopy(row['candidate'])
            if not isinstance(c, dict) or 'candidate_impact_fragment' not in c:
                raise ValueError('candidate missing fragment')
            quotes = [x['quote'] for x in fact['evidence'] if x['source_type']=='memory']
            row['fragment_match'] = locate_fragment(split['memory_text'], c['candidate_impact_fragment'], quotes)
            if row['fragment_match']['located'] is None:
                raise ValueError('candidate fragment cannot be uniquely located in fact memory evidence: ' + row['fragment_match']['method'])
            c['candidate_impact_fragment'] = row['fragment_match']['located']
            row['located_candidate'] = c
            row['validation'] = v1.validate_candidate(c, split, fact, new_map)
            row['status'] = 'ok'
        except Exception as e:
            row['errors'].append({'stage':stage,'type':type(e).__name__,'message':str(e)})
            result['status'] = 'partial_or_error'
        result['results'].append(row)
    return result
