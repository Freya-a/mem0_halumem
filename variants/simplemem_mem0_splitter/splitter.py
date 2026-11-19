"""SimpleMem-derived memory extraction for evidence-preserving local updates.

Adapted from SimpleMem (c) 2025 AIMING Lab; see LICENSE and SOURCE.md.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class MemoryEntry:
    """Adapted semantic and symbolic layers of SimpleMem's MemoryEntry."""
    unit_id: str                         # entry_id
    raw_statement: str                   # lossless_restatement, memory only
    contextualized_statement: str       # lossless_restatement, resolved when supported
    memory_quotes: list[str]
    context_quotes: list[str]
    entities: list[str]
    condition: Optional[str]
    valid_time: Optional[str]            # timestamp, factual validity only


def build_extraction_prompt(memory_id: str, memory_text: str, source_context: Optional[str] = None) -> str:
    # Adapted from MemoryBuilder._build_extraction_prompt: preserve its complete
    # coverage, lossless restatement, structured metadata and output format.
    # Its forced resolution and absolute-time conversion are deliberately removed.
    return f'''Your task is to extract all valuable information from the following old memory and convert it into structured memory entries.

[Old Memory ID]
{json.dumps(memory_id, ensure_ascii=False)}
[Old Memory]
{json.dumps(memory_text, ensure_ascii=False)}
[Optional source context, only for necessary and supported disambiguation]
{json.dumps(source_context, ensure_ascii=False)}

[Requirements]
1. Complete Coverage: Generate enough memory entries to ensure ALL information in the old memory is captured. Split independently assessable facts while preserving subjects, objects, relationships, conditions, reasons, negation and uncertainty. Do not overstate attributed opinions as objective facts.
2. Lossless Information: raw_statement must express only what the old memory says; retain unresolved pronouns and relative time when necessary. contextualized_statement may resolve references only when reliably supported by source context; otherwise keep the ambiguity and add it to unresolved. Never use new evidence as a source.
3. Each memory_quotes entry must be a nonempty exact contiguous verbatim substring of the old memory, with enough quotations to support the unit. Use multiple substrings where needed. If source context was needed for resolution include exact verbatim context_quotes; otherwise use [].
4. entities include only explicit or reliably disambiguated entities. condition and valid_time are strings or null. Set valid_time to null unless the memory explicitly states a fact's valid time; a recording timestamp is not necessarily a fact's valid time. Never infer or invent an absolute time.
5. Output a single valid JSON object without markdown or explanations. Every unit has a nonempty unique unit_id. List unresolved issues as strings. If a candidate cannot be supported, record the issue rather than inventing evidence.

[Output Format]
{{"memory_id": {json.dumps(memory_id, ensure_ascii=False)}, "original_text": {json.dumps(memory_text, ensure_ascii=False)}, "units": [{{"unit_id":"u1", "raw_statement":"...", "contextualized_statement":"...", "memory_quotes":["..."], "context_quotes":[], "entities":[], "condition":null, "valid_time":null}}], "unresolved":[]}}
'''


def extract_json(text: str):
    """Adapted direct/fenced JSON paths from SimpleMem LLMClient.extract_json.

    Do not repair malformed JSON or silently extract a fragment from prose.
    """
    if not text or not text.strip():
        raise ValueError('Empty response received')
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    if text.lower().startswith('```json') and text.endswith('```'):
        return json.loads(text[7:-3].strip())
    if text.startswith('```') and text.endswith('```'):
        return json.loads(text[3:-3].strip())
    raise ValueError('Response is not valid JSON')


def parse_and_validate(response: str, memory_id: str, memory_text: str, source_context: Optional[str] = None) -> dict:
    errors, warnings, locations = [], [], []
    result = {'status': 'failed', 'parsed': None, 'errors': errors, 'warnings': warnings, 'quote_locations': locations,
              'semantic_check': 'not_automatically_verified', 'validated_units': [], 'entity_normalizations': []}
    try:
        data = extract_json(response)
        result['parsed'] = data
    except (ValueError, TypeError) as exc:
        errors.append('JSON parse failed: ' + str(exc))
        return result
    if not isinstance(data, dict):
        errors.append('top-level JSON must be an object')
        return result
    for key in ('memory_id', 'original_text', 'units', 'unresolved'):
        if key not in data: errors.append(f'missing required field {key}')
    if not isinstance(memory_id, str) or not memory_id.strip() or data.get('memory_id') != memory_id:
        errors.append('invalid or mismatched memory_id')
    if data.get('original_text') != memory_text: errors.append('original_text differs from input')
    unresolved = data.get('unresolved')
    if not isinstance(unresolved, list) or any(not isinstance(x, str) or not x.strip() for x in unresolved):
        errors.append('unresolved must be a list of nonempty strings')
    elif unresolved: warnings.append('unresolved issues reported by model')
    units = data.get('units')
    if not isinstance(units, list) or not units:
        errors.append('units must be a nonempty list')
        return result
    seen = set()
    required = ('unit_id','raw_statement','contextualized_statement','memory_quotes','context_quotes','entities','condition','valid_time')
    for i, item in enumerate(units):
        entry_error_count = len(errors)
        label = f'units[{i}]'
        if not isinstance(item, dict):
            errors.append(f'{label} must be an object'); continue
        for key in required:
            if key not in item: errors.append(f'{label} missing {key}')
        uid = item.get('unit_id')
        if not isinstance(uid,str) or not uid.strip() or uid in seen: errors.append(f'{label} invalid or duplicate unit_id')
        else: seen.add(uid)
        for key in ('raw_statement','contextualized_statement'):
            if not isinstance(item.get(key),str) or not item[key].strip(): errors.append(f'{label}.{key} must be a nonempty string')
        for key in ('condition','valid_time'):
            if key in item and item[key] is not None and (not isinstance(item[key],str) or not item[key].strip()): errors.append(f'{label}.{key} must be null or a nonempty string')
        normalized_entities = []
        for key in ('memory_quotes','context_quotes','entities'):
            val = item.get(key)
            if key == 'entities':
                if not isinstance(val, list):
                    errors.append(f'{label}.entities must be a list'); continue
                for j, entity in enumerate(val):
                    if isinstance(entity, str) and entity.strip():
                        normalized_entities.append(entity)
                    elif isinstance(entity, dict) and isinstance(entity.get('name'), str) and entity['name'].strip():
                        normalized_entities.append(entity['name'])
                        result['entity_normalizations'].append({
                            'unit_index': i, 'unit_id': uid, 'entity_index': j,
                            'original': entity, 'normalized': entity['name']})
                        warnings.append(f'{label}.entities[{j}] normalized from object; review retained original metadata')
                    else:
                        errors.append(f'{label}.entities[{j}] must be a nonempty string or object with a nonempty string name')
                continue
            if not isinstance(val,list) or any(not isinstance(q,str) or not q.strip() for q in val):
                errors.append(f'{label}.{key} must be a list of nonempty strings'); continue
            if key == 'memory_quotes' and not val: errors.append(f'{label}.memory_quotes must not be empty')
            source = memory_text if key == 'memory_quotes' else source_context or ''
            for j, quote in enumerate(val):
                # Find overlapping matches as well; spans are Python character offsets.
                offsets, start = [], 0
                while (pos := source.find(quote, start)) != -1:
                    offsets.append([pos, pos + len(quote)]); start = pos + 1
                locations.append({'unit_id': uid, 'field': key, 'index': j, 'spans': offsets})
                if not offsets: errors.append(f'{label}.{key}[{j}] not found verbatim in source')
                elif len(offsets) > 1: warnings.append(f'{label}.{key}[{j}] ambiguous: {len(offsets)} occurrences')
        if item.get('contextualized_statement') != item.get('raw_statement') and not item.get('context_quotes'):
            warnings.append(f'{label}: changed contextualized_statement without context quotes; check whether disambiguation was used')
        if len(errors) == entry_error_count:
            values = {key: item[key] for key in required}
            values['entities'] = normalized_entities
            result['validated_units'].append(asdict(MemoryEntry(**values)))
    result['status'] = 'failed' if errors else 'needs_review' if warnings else 'passed'
    return result
