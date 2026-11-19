"""Controlled v2: retain the baseline prompt and append explicit evidence rules."""
from splitter import build_extraction_prompt


def build_extraction_prompt_v2(memory_id: str, memory_text: str, source_context: str | None = None) -> str:
    baseline = build_extraction_prompt(memory_id, memory_text, source_context)
    return baseline + '''
[Additional evidence and scope checks — apply to every unit]
- Quote directly and verbatim from the corresponding source: each quote must be an exact continuous substring, preserving every character, capitalization and punctuation. Never stitch separate words into one quote. When the subject, relation or antecedent is elsewhere, include multiple exact substrings or a longer exact substring. Before returning, check each quote against its source. If evidence is insufficient, report the issue in unresolved rather than inventing a quote.
- Preserve attribution in BOTH raw_statement and contextualized_statement. A person's preference, opinion, stated reason, belief or assessment remains that person's stated view; do not convert it into an unattributed objective fact. Keep the source's uncertainty, negation, reasons and relations. Do not add a claim about what a person believes unless the original supports that attribution.
- Make each unit understandable as an individually assessable relation with its necessary subject, predicate and object, retaining essential qualifiers and attribution. Do not output an isolated fragment without its relation. Avoid duplicate or fully subsumed units that repeat the same proposition with no distinct independently assessable content. Split independently assessable content when supported; do not merge unrelated propositions merely to reduce count, and do not split away required conditions or reasons.
- condition is ONLY an explicit applicability condition or explicit hypothetical/concessive condition from the memory. A cause, explanation or motivation is not a condition: keep it in the statement and set condition to null if no condition is stated. Preserve hypothetical and concessive wording without turning it into a claim the condition occurred.
- Resolve a reference only when it is reliably established by the memory or provided source context. If the identity or antecedent is unresolved, retain the ambiguous reference or a non-identifying description in BOTH statements, do not assert a specific identity for that reference in entities, and record the specific uncertainty once in unresolved. Do not assert a resolution and list the same resolution as uncertain. If a resolution needs source_context, quote its exact support in context_quotes; otherwise do not invent context.
- valid_time is null unless a fact's valid time is explicitly stated. A recording timestamp alone is not its valid time. Check that unresolved contains only actual unresolved issues and is consistent with the units.
'''
