"""One-shot OpenAI-compatible adapter using the project's existing configuration.

No Mem0 import, dataset access, model discovery, or fallback model is included.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import math
import os
from pathlib import Path
import re
import shlex
from typing import Any, Mapping
from urllib.parse import urlsplit

from splitter import ValidationError, _unique_json_object

ALIASES = {
    "LLM_BASE_URL": ("LLM_BASE_URL", "OPENAI_BASE_URL"),
    "LLM_API_KEY": ("LLM_API_KEY", "OPENAI_API_KEY"),
    "LLM_MODEL": ("LLM_MODEL", "OPENAI_MODEL"),
}
OPTIONAL = ("OPENAI_MAX_TOKENS", "OPENAI_TEMPERATURE", "OPENAI_TIMEOUT")


@dataclass
class ModelSettings:
    model: str
    api_key: str = field(repr=False)
    base_url: str = field(repr=False)
    timeout: float = 180.0
    generation: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)


def _usable(value: Any) -> bool:
    return (isinstance(value, str) and bool(value)
            and not re.fullmatch(r"[\s*<>]+", value)
            and not any(token in value.lower() for token in ("your_", "your-", "placeholder", "env:", "${")))


def load_model_settings(env_file: Path, environ: Mapping[str, str] | None = None) -> ModelSettings:
    """Read only the specified config file; preserve local_smoke alias/priority rules."""
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        raise ValidationError("missing_configuration", "$config", "Cannot read the specified configuration file.") from None
    values, sources = {}, {}
    for number, line in enumerate(lines, 1):
        line = line.strip().removeprefix("export ")
        if not line or line.startswith("#"):
            continue
        key, separator, raw = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", key.strip()):
            raise ValidationError("invalid_configuration", "$config", f"Invalid assignment at line {number}; values hidden.")
        try:
            tokens = shlex.split(raw, comments=True)
        except ValueError:
            raise ValidationError("invalid_configuration", "$config", f"Invalid quoting at line {number}; values hidden.") from None
        if len(tokens) > 1:
            raise ValidationError("invalid_configuration", "$config", f"Unquoted value at line {number}; values hidden.")
        value = tokens[0] if tokens else ""
        if _usable(value):
            values[key.strip()] = value
            sources[key.strip()] = str(env_file)
    environment = os.environ if environ is None else environ
    relevant = {name for aliases in ALIASES.values() for name in aliases} | set(OPTIONAL)
    for key in relevant:
        if _usable(environment.get(key)):
            values[key], sources[key] = environment[key], "process environment"
    selected, provenance = {}, {}
    for target, aliases in ALIASES.items():
        for alias in aliases:
            if _usable(values.get(alias)):
                selected[target] = values[alias]
                provenance[target] = {"variable": alias, "source": sources[alias]}
                break
    missing = [key for key in ALIASES if key not in selected]
    if missing:
        raise ValidationError("missing_configuration", "$config", "Missing usable settings: " + ", ".join(missing))
    try:
        endpoint = urlsplit(selected["LLM_BASE_URL"])
        valid_endpoint = (endpoint.scheme in ("http", "https") and endpoint.hostname
                          and not endpoint.username and not endpoint.password
                          and not endpoint.query and not endpoint.fragment)
    except ValueError:
        valid_endpoint = False
    if not valid_endpoint:
        raise ValidationError("invalid_configuration", "$config.LLM_BASE_URL", "Invalid endpoint; value hidden.")
    generation = {}
    timeout = 180.0  # Same default timeout as scripts/local_smoke.py.
    for name in OPTIONAL:
        if name not in values:
            continue
        try:
            value = int(values[name]) if name == "OPENAI_MAX_TOKENS" else float(values[name])
            if not math.isfinite(value) or (name != "OPENAI_TEMPERATURE" and value <= 0) or (name == "OPENAI_TEMPERATURE" and not 0 <= value <= 2):
                raise ValueError
        except (ValueError, OverflowError):
            raise ValidationError("invalid_configuration", "$config."+name, "Invalid numeric setting; value hidden.") from None
        if name == "OPENAI_TIMEOUT":
            timeout = value
        else:
            generation["max_tokens" if name == "OPENAI_MAX_TOKENS" else "temperature"] = value
        provenance[name] = {"variable": name, "source": sources[name]}
    return ModelSettings(model=selected["LLM_MODEL"], api_key=selected["LLM_API_KEY"],
                         base_url=selected["LLM_BASE_URL"], timeout=timeout,
                         generation=generation, provenance=provenance)


def load_design_prompt(path: Path) -> str:
    try:
        design = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        raise ValidationError("prompt_unavailable", "$prompt", "Cannot read DESIGN.md.") from None
    matches = re.findall(r"```text\n(.*?)\n```", design, flags=re.S)
    if len(matches) != 1 or not matches[0].strip():
        raise ValidationError("prompt_unavailable", "$prompt", "Expected exactly one nonempty text prompt block in DESIGN.md.")
    return matches[0]


class OpenAICompatibleBackend:
    """At most one SDK create call; returned content is parsed without repairs."""

    def __init__(self, settings: ModelSettings, prompt: str, client: Any = None):
        self.settings = settings
        self.prompt = prompt
        self.call_count = 0
        self.raw_content = None
        self.response_metadata = {}
        self._owns_client = client is None
        if client is None:
            try:
                import httpx
                from openai import OpenAI
            except ImportError:
                raise ValidationError("missing_dependency", "$client", "Existing openai/httpx packages are required; nothing installed.") from None
            for name in ("openai", "httpx", "httpcore"):
                logging.getLogger(name).setLevel(logging.WARNING)
            client = OpenAI(api_key=settings.api_key, base_url=settings.base_url,
                            max_retries=0, timeout=settings.timeout,
                            http_client=httpx.Client(follow_redirects=False, timeout=settings.timeout))
        if client.max_retries != 0 or client._client.follow_redirects:
            raise ValidationError("unsafe_client_configuration", "$client", "Retries and redirects must be disabled.")
        self.client = client

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        if self.call_count:
            raise ValidationError("call_limit_reached", "$model", "This backend already attempted one request; no retry permitted.")
        self.call_count += 1
        try:
            completion = self.client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "system", "content": self.prompt},
                          {"role": "user", "content": json.dumps(request, ensure_ascii=False)}],
                response_format={"type": "json_object"},
                **self.settings.generation,
            )
        except Exception as error:
            # Do not include provider response bodies, URLs or exception strings:
            # these may contain credentials. Preserve safe diagnostic fields only.
            status = getattr(error, "status_code", None)
            self.response_metadata = {"error_type": type(error).__name__, "http_status": status}
            raise ValidationError("model_request_failed", "$model",
                                  f"{type(error).__name__}; HTTP status={status}; not retried; provider message hidden.") from None
        try:
            choice = completion.choices[0]
            self.raw_content = choice.message.content
            self.response_metadata = {
                "returned_model": completion.model,
                "finish_reason": choice.finish_reason,
                "usage": {name: getattr(completion.usage, name, None)
                          for name in ("prompt_tokens", "completion_tokens", "total_tokens")},
            }
        except (AttributeError, IndexError, TypeError):
            raise ValidationError("invalid_model_response", "$model", "Response has no usable assistant choice.") from None
        if choice.finish_reason != "stop":
            raise ValidationError("model_incomplete_response", "$model", "Response did not finish normally; not retried.")
        if not isinstance(self.raw_content, str) or not self.raw_content.strip():
            raise ValidationError("empty_model_response", "$model", "Assistant returned no text; not retried.")
        try:
            return json.loads(self.raw_content, object_pairs_hook=_unique_json_object)
        except json.JSONDecodeError:
            raise ValidationError("model_json_error", "$model.content", "Model content is not strict JSON; not repaired or retried.") from None
