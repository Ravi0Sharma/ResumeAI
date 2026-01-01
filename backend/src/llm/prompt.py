"""Prompt construction for LLM analysis (domain layer)."""

from __future__ import annotations

PROMPT_TEMPLATE = (
    "Du är en resume analyzer.\n"
    "Svara ENDAST med giltig JSON.\n"
    "Inga förklaringar. Ingen text utanför JSON.\n\n"
    "### Input:\n"
    "Match the resume to the job description and return structured JSON with this schema:\n"
    "{\n"
    '  "score": <integer 0-1000>,\n'
    '  "tips": [\n'
    '    {"id": <string>, "message": <string>, "severity": <"GOOD"|"WARNING"|"NEEDS_WORK">}\n'
    "  ],\n"
    '  "analysis": <object>\n'
    "}\n\n"
    "Resume:\n"
    "{{RESUME_TEXT}}\n\n"
    "Job Description:\n"
    "{{JOB_TEXT}}\n\n"
    "### Output:\n"
)


def build_prompt(cv_text: str, job_text: str) -> str:
    return PROMPT_TEMPLATE.replace("{{RESUME_TEXT}}", cv_text).replace("{{JOB_TEXT}}", job_text)


