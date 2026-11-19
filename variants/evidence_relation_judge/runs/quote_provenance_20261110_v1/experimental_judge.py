"""Experimental prompt only; v2 request validation and result validation are unchanged."""
import relation_judge_v2 as v2

PROVENANCE_INSTRUCTION = '''
旧引文来源核对：old_quote 只能逐字复制当前 fact.evidence 中 source_type 为 "memory" 且 source_id 等于 memory_id 的 quote 的非空连续原文，并且该引文属于 memory_text。先检查 source_type，再复制；不能从 source_type 为 "context" 的 quote、source_context 或 contextualized_subfact 复制 old_quote，即使上下文与旧记忆含义相同也不行。不得改写人称、大小写或标点，不得拼接不同来源。旧上下文可用于理解主体与条件，但不能当作旧记忆原文引用。
如果旧记忆不能支持某项所需表述，要在理由或待确认问题中如实说明，不能借用旧上下文伪造旧记忆支持；若没有合法的旧记忆引文，不能编造或替换引文，应保留无法通过校验的结果。'''
SYSTEM = v2.SYSTEM + PROVENANCE_INSTRUCTION
LABELS = v2.LABELS
judge = v2.judge
