#!/usr/bin/env python3
"""One-call DnD-inspired splitter using the existing baseline schema."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Callable

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
MODEL = 'qwen-plus-2025-12-01'
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from splitter import ValidationError, _read_json, split_memory  # noqa: E402


def split_memory_v8(request: dict, backend_factory: Callable) -> dict:
    """Run one prompt-bound backend and validate with the existing splitter.

    The factory takes the v8 prompt and returns a callable accepting the memory
    request. The model's claims remain candidates; validation is structural and
    verifies literal provenance, not semantic correctness or atomicity.
    """
    try:
        prompt = (HERE / 'prompt.txt').read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ValidationError('prompt_unavailable', '$prompt', 'Cannot read v8 prompt.') from error
    backend = backend_factory(prompt)
    try:
        return split_memory(request, backend)
    finally:
        close = getattr(backend, 'close', None)
        if callable(close):
            close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Split one old memory using the v8 DnD-inspired prompt.')
    parser.add_argument('--input', required=True, type=Path, help='Input JSON with memory_id, memory_text and optional source_context.')
    parser.add_argument('--env-file', required=True, type=Path, help='Existing OpenAI-compatible model configuration file.')
    args = parser.parse_args(argv)
    try:
        from real_backend import OpenAICompatibleBackend, load_model_settings
        request = _read_json(args.input)
        settings = load_model_settings(args.env_file, environ={**os.environ, 'LLM_MODEL': MODEL})
        result = split_memory_v8(request, lambda prompt: OpenAICompatibleBackend(settings, prompt))
    except ValidationError as error:
        print(json.dumps({'error': error.as_dict()}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
