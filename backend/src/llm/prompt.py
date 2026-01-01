"""Prompt construction for LLM analysis (domain layer)."""

from __future__ import annotations

PROMPT_TEMPLATE = PROMPT_TEMPLATE = (
    "You are a resume analyzer.\n"
    "Respond ONLY with valid JSON.\n"
    "No markdown. No text outside the JSON object.\n\n"

    "### Task:\n"
    "Compare the resume to the job description and return structured JSON using the schema below.\n"
    "If information is missing, make reasonable assumptions based on the available text.\n\n"

    "### Schema (must be followed exactly):\n"
    "{\n"
    '  "score": <integer between 0 and 1000>,\n'
    '  "tips": [\n'
    '    {\n'
    '      "id": <string, short and stable identifier>,\n'
    '      "message": <string, concrete improvement suggestion>,\n'
    '      "severity": <\"GOOD\" | \"WARNING\" | \"NEEDS_WORK\">\n'
    '    }\n'
    "  ],\n"
    '  "analysis": <object or empty object {}>\n'
    "}\n\n"

    "Rules:\n"
    "- Return an empty array if no improvements are needed.\n"
    "- `analysis` may be `{}` if there is nothing additional to include.\n"
    "- Do not include any text outside the JSON object.\n\n"

    "Resume:\n"
    "{{RESUME_TEXT}}\n\n"
    "Job Description:\n"
    "{{JOB_TEXT}}\n\n"
    "### Output:\n"
)


def build_prompt(cv_text: str, job_text: str) -> str:
    return PROMPT_TEMPLATE.replace("{{RESUME_TEXT}}", cv_text).replace("{{JOB_TEXT}}", job_text)


