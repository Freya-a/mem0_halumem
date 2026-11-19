"""Strict-label experimental judge: mixed evidence is review-only, never relabeled.

Component 2 can consume normal rows unchanged; a mixed row follows its existing
upstream-error path. The sidecar is a model candidate, not semantic validation.
"""
import relation_judge_v2 as v2
import relation_judge_v4 as v4

LABELS = v2.LABELS
_MIXED_V4 = '2. 新证据同时支持旧内容且增加相关实质信息、没有历史纠错或阶段变化时，既不符合只含支持的 support，也不符合不支持旧事实的 supplement。既有单标签无法完整表达时用 uncertain 表示分类表达不足；reason 分别说出受支持的旧内容和新增内容，并说明保留旧内容；confirmation_questions 询问如何分别记录两部分。不要暗示已知事实本身未经确认，也不要因为有新增就当作旧事实被推翻。该规则不扩展其他标签的定义。'
_MIXED_V5 = '''2. 新证据同时支持旧内容且增加相关实质信息、没有历史纠错或阶段变化时，既不符合只含支持的 support，也不符合不支持旧事实的 supplement；不能把证据充分的混合情况塞进 uncertain。例外地在 relation 填 mixed_unrepresentable，reason 分别说明支持的旧内容、具体新增信息和保留旧内容，不声称事实本身不明；这是供程序拦截并留待复核的标记，不是现有六标签之一，不构成可供组件二采用的有效候选。其余字段照常输出、引文照常复制。其他情况只能选原有六标签。'''
if v4.SYSTEM.count(_MIXED_V4) != 1:
    raise RuntimeError('unexpected v4 prompt; cannot construct strict v5 prompt')
SYSTEM = v4.SYSTEM.replace(_MIXED_V4, _MIXED_V5)


def judge(data, backend):
    result = v2.judge(data, backend)
    for row in result.get('results', []):
        candidate = row.get('candidate')
        if isinstance(candidate, dict) and candidate.get('relation') == 'mixed_unrepresentable':
            row['mixed_relation'] = {'status': 'unrepresentable_in_v2_schema',
                'reason_candidate': candidate.get('reason'), 'semantic_correctness': 'not_checked',
                'effect': 'upstream_error_for_component2'}
    return result
