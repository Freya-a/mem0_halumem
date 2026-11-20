"""One-request Qwen backend using the existing experiment's file-only configuration."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'simplemem_mem0_splitter'))
from run_file_priority import choose_file_settings, create_http_client
from dotenv import dotenv_values
from openai import OpenAI

MODEL = 'qwen-plus-2025-12-01'


class QwenBackend:
    def __init__(self, *, client=None):
        self.http = None
        self.provider_response = None
        if client is not None:
            self.client = client
            return
        key, workspace = choose_file_settings(dotenv_values(ROOT / '.env.server.medium-full'))
        if not key or not workspace or not re.fullmatch(r'(?:llm|ws)-[a-zA-Z0-9-]+', workspace):
            raise ValueError('missing or invalid file-only Qwen configuration')
        profile = json.loads((ROOT / 'config/medium_full_qwen_plus_20251201.json').read_text(encoding='utf-8'))
        base_url = profile['llm']['config']['openai_base_url'].replace('{DASHSCOPE_WORKSPACE_ID}', workspace)
        self.http = create_http_client()
        self.client = OpenAI(api_key=key, base_url=base_url, max_retries=0, timeout=180.0, http_client=self.http)

    def __call__(self, messages):
        response = self.client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0, response_format={'type': 'json_object'}, max_tokens=8192)
        self.provider_response = response.model_dump(mode='json')
        return {'content': response.choices[0].message.content if response.choices else None,
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason if response.choices else None}

    def close(self):
        if self.http is not None:
            self.http.close()
