#!/usr/bin/env python3
"""v9 fact splitting with a separately validated employment-component sidecar."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from typing import Callable

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from splitter import ValidationError, _object, _list, _string, split_memory

MODEL = 'qwen-plus-2025-12-01'
V9_PROMPT = HERE.parent / 'v9_local_update' / 'prompt.txt'


def get_prompt() -> str:
    try:
        return V9_PROMPT.read_text(encoding='utf-8') + '\n\n' + (HERE / 'components_prompt.txt').read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ValidationError('prompt_unavailable', '$prompt', 'Cannot read frozen prompt sources.') from error


def _validate_components(components, request, facts):
    contexts = {item['source_id']: item['text'] for item in request.get('source_context', [])}
    seen = set()
    for i, item in enumerate(_list(components, '$.employment_components')):
        path = f'$.employment_components[{i}]'
        _object(item, path, ('fact_index', 'employer', 'position', 'relationship'))
        index = item['fact_index']
        if type(index) is not int or index < 1 or index > len(facts) or index in seen:
            raise ValidationError('invalid_fact_index', path + '.fact_index', 'Expected a unique existing fact index.')
        seen.add(index)
        for key in ('employer', 'position', 'relationship'):
            element = item[key]
            element_path = path + '.' + key
            _object(element, element_path, ('status', 'source_type', 'source_id', 'quote'))
            if element['status'] == 'pending':
                if any(element[k] is not None for k in ('source_type', 'source_id', 'quote')):
                    raise ValidationError('invalid_value', element_path, 'Pending fields must be null.')
                continue
            if element['status'] != 'located':
                raise ValidationError('invalid_value', element_path + '.status', 'Expected located or pending.')
            for field in ('source_type', 'source_id', 'quote'):
                _string(element[field], element_path + '.' + field)
            if element['source_type'] == 'memory' and element['source_id'] == request['memory_id']:
                text = request['memory_text']
            elif element['source_type'] == 'context' and element['source_id'] in contexts:
                text = contexts[element['source_id']]
            else:
                raise ValidationError('unknown_source', element_path + '.source_id', 'Source does not match the request.')
            if element['quote'] not in text:
                raise ValidationError('quote_not_found', element_path + '.quote', 'Quote must be an exact source substring.')
        if item['relationship']['status'] == 'located' and any(item[k]['status'] != 'located' for k in ('employer', 'position')):
            raise ValidationError('invalid_relationship', path + '.relationship', 'Both components must be located before the relationship.')


def split_memory_v10(request: dict, backend_factory: Callable) -> dict:
    backend = backend_factory(get_prompt())
    components_holder = []

    def adapt(snapshot):
        response = deepcopy(backend(snapshot))
        _object(response, '$', ('facts', 'employment_components'), ('memory_id', 'memory_text'))
        components_holder.append(response.pop('employment_components'))
        return response

    try:
        result = split_memory(request, adapt)
        _validate_components(components_holder[0], request, result['facts'])
        result['employment_components'] = components_holder[0]
        return result
    finally:
        close = getattr(backend, 'close', None)
        if callable(close):
            close()
