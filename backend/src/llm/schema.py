"""Pydantic schema + validation helpers for expected LLM output JSON."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


Severity = Literal["GOOD", "WARNING", "NEEDS_WORK"]


class Tip(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    message: str
    severity: Severity


class AnalyzeResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0, le=1000)
    tips: List[Tip]
    analysis: Optional[Dict[str, Any]] = None


def validate_analyze_result(data: Any) -> AnalyzeResult:
    return AnalyzeResult.model_validate(data)


