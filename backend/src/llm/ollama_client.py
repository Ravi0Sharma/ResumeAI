"""
Ollama client (domain layer).

Pure transport: given config + prompt, returns raw model string (no JSON parsing).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


DEFAULT_OLLAMA_URL = "http://host.docker.internal:11434"
DEFAULT_OLLAMA_MODEL = "html-model:latest"


@dataclass(frozen=True)
class OllamaSettings:
    ollama_url: str
    ollama_model: str


def get_settings() -> OllamaSettings:
    ollama_url = os.getenv("OLLAMA_URL", DEFAULT_OLLAMA_URL).rstrip("/")
    ollama_model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    return OllamaSettings(ollama_url=ollama_url, ollama_model=ollama_model)


def generate(prompt: str, *, settings: OllamaSettings | None = None) -> str:
    """
    Call Ollama /api/generate and return the raw string response payload.

    Raises:
        RuntimeError with args compatible with previous API behavior:
        - ("OLLAMA_HTTP_ERROR", details)
        - ("OLLAMA_UNREACHABLE", details)
        - ("OLLAMA_REQUEST_FAILED", details)
    """
    if settings is None:
        settings = get_settings()

    url = f"{settings.ollama_url}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        raise RuntimeError("OLLAMA_HTTP_ERROR", body or str(e)) from e
    except urllib.error.URLError as e:
        raise RuntimeError("OLLAMA_UNREACHABLE", str(e)) from e
    except Exception as e:
        raise RuntimeError("OLLAMA_REQUEST_FAILED", str(e)) from e

    try:
        parsed = json.loads(body)
    except Exception:
        # Ollama should return JSON; if not, surface raw body.
        return body

    # Ollama /api/generate typically returns {"response": "...", ...}
    if isinstance(parsed, dict) and isinstance(parsed.get("response"), str):
        return parsed["response"]
    return body


