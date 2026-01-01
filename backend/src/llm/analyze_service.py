"""
End-to-end LLM analysis service (domain layer).

Responsibilities:
- Build prompt
- Call Ollama
- Parse + validate JSON
- Return typed result or raise a domain error
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

from pydantic import ValidationError

from . import ollama_client
from .prompt import build_prompt
from .schema import AnalyzeResult, validate_analyze_result


@dataclass(frozen=True)
class DomainError(Exception):
    code: str
    message: Optional[str] = None
    details: Any = None


def analyze(cv_text: str, job_text: str) -> AnalyzeResult:
    prompt = build_prompt(cv_text, job_text)
    raw = ollama_client.generate(prompt)
    raw = (raw or "").strip()

    try:
        model_json = json.loads(raw)
    except Exception:
        # Preserve existing API behavior: invalid JSON => code only.
        raise DomainError(code="INVALID_MODEL_OUTPUT") from None

    if not isinstance(model_json, dict):
        raise DomainError(code="INVALID_MODEL_OUTPUT", message="Expected JSON object")

    score = model_json.get("score")
    tips = model_json.get("tips")

    if not isinstance(score, int) or score < 0 or score > 1000:
        raise DomainError(code="INVALID_MODEL_OUTPUT", message="Invalid score", details={"score": score})

    if not isinstance(tips, list) or not all(isinstance(t, dict) for t in tips):
        raise DomainError(code="INVALID_MODEL_OUTPUT", message="Invalid tips", details={"tips": tips})

    for tip in tips:
        if (
            not isinstance(tip.get("id"), str)
            or not isinstance(tip.get("message"), str)
            or not isinstance(tip.get("severity"), str)
        ):
            raise DomainError(code="INVALID_MODEL_OUTPUT", message="Invalid tip shape", details={"tip": tip})

    analysis = model_json.get("analysis")
    if analysis is not None and not isinstance(analysis, dict):
        raise DomainError(code="INVALID_MODEL_OUTPUT", message="Invalid analysis", details={"analysis": analysis})

    # Strict schema validation (forbid extras, enforce severity enum, etc.)
    try:
        return validate_analyze_result(model_json)
    except ValidationError as e:
        raise DomainError(code="INVALID_MODEL_OUTPUT", message="Invalid model output", details=e.errors()) from None


