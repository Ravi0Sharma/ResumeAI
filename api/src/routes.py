"""API routes for resume parsing."""

import tempfile
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import get_settings

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SCORE = 1000


def _compute_score_and_tips_from_normalized_resume(normalized: dict) -> tuple[int, list[dict]]:
    """
    Deterministically compute score + tips from parsed resume content.

    This MUST be driven only by extracted resume data (no mocks/randomness).
    """
    def _count_list(key: str) -> int:
        v = normalized.get(key)
        if isinstance(v, list):
            return len([x for x in v if isinstance(x, str) and x.strip()])
        return 0

    def _has_str(key: str) -> bool:
        v = normalized.get(key)
        return isinstance(v, str) and bool(v.strip())

    tips: list[dict] = []

    # Presence checks
    if not _has_str("name"):
        tips.append({"id": "name", "message": "Missing name", "severity": "NEEDS_WORK"})
    if not _has_str("email"):
        tips.append({"id": "email", "message": "Missing email", "severity": "NEEDS_WORK"})
    if not _has_str("mobile_number"):
        tips.append({"id": "mobile_number", "message": "Missing phone number", "severity": "NEEDS_WORK"})

    skills_count = _count_list("skills")
    if skills_count < 5:
        tips.append(
            {
                "id": "skills",
                "message": f"Low skills coverage (found {skills_count})",
                "severity": "WARNING" if skills_count >= 3 else "NEEDS_WORK",
            }
        )

    degree_count = _count_list("degree")
    if degree_count == 0:
        tips.append({"id": "education", "message": "Education not detected", "severity": "WARNING"})

    company_count = _count_list("company_names")
    if company_count == 0:
        tips.append({"id": "experience", "message": "Work experience not detected", "severity": "WARNING"})

    total_experience = normalized.get("total_experience")
    if total_experience is None:
        tips.append({"id": "total_experience", "message": "Total experience not detected", "severity": "WARNING"})

    pages = normalized.get("no_of_pages")
    if isinstance(pages, int) and pages > 2:
        tips.append({"id": "length", "message": f"Resume is {pages} pages (consider shortening)", "severity": "WARNING"})

    # Score is computed from field completeness + skills density.
    weights = {
        "name": 1.0,
        "email": 1.0,
        "mobile_number": 1.0,
        "skills": 2.0,
        "education": 1.0,
        "experience": 1.0,
        "total_experience": 1.0,
        "length": 0.5,
    }

    earned = 0.0
    possible = sum(weights.values())

    earned += weights["name"] if _has_str("name") else 0.0
    earned += weights["email"] if _has_str("email") else 0.0
    earned += weights["mobile_number"] if _has_str("mobile_number") else 0.0

    earned += weights["education"] if degree_count > 0 else 0.0
    earned += weights["experience"] if company_count > 0 else 0.0
    earned += weights["total_experience"] if total_experience is not None else 0.0

    # Skills: scale up to 10 skills, then cap.
    earned += weights["skills"] * min(1.0, skills_count / 10.0)

    # Length: 1.0 if <=2 pages, 0.5 if unknown, 0.0 if >2 pages.
    if isinstance(pages, int):
        earned += weights["length"] if pages <= 2 else 0.0
    else:
        earned += weights["length"] * 0.5

    score = int(round(MAX_SCORE * (earned / possible))) if possible > 0 else 0
    score = max(0, min(MAX_SCORE, score))

    return score, tips


class AnalyzeRequest(BaseModel):
    cv_text: str
    job_text: str


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


def build_prompt(resume_text: str, job_text: str) -> str:
    return (
        PROMPT_TEMPLATE.replace("{{RESUME_TEXT}}", resume_text).replace("{{JOB_TEXT}}", job_text)
    )


def _error(code: str, message: str, *, details=None, status_code: int = 500) -> JSONResponse:
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def _ollama_generate(prompt: str) -> str:
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


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    cv_text = (req.cv_text or "").strip()
    job_text = (req.job_text or "").strip()
    if not cv_text or not job_text:
        return _error(
            "BAD_REQUEST",
            "cv_text and job_text are required",
            details={"cv_text": bool(cv_text), "job_text": bool(job_text)},
            status_code=400,
        )

    prompt = build_prompt(cv_text, job_text)

    try:
        raw = _ollama_generate(prompt)
        raw = (raw or "").strip()
        try:
            model_json = json.loads(raw)
        except Exception:
            return JSONResponse(
                status_code=502,
                content={"ok": False, "error": {"code": "INVALID_MODEL_OUTPUT"}},
            )
        if not isinstance(model_json, dict):
            return _error("INVALID_MODEL_OUTPUT", "Expected JSON object", status_code=502)

        score = model_json.get("score")
        tips = model_json.get("tips")

        if not isinstance(score, int) or score < 0 or score > 1000:
            return _error("INVALID_MODEL_OUTPUT", "Invalid score", details={"score": score}, status_code=502)

        if not isinstance(tips, list) or not all(isinstance(t, dict) for t in tips):
            return _error("INVALID_MODEL_OUTPUT", "Invalid tips", details={"tips": tips}, status_code=502)

        for tip in tips:
            if not isinstance(tip.get("id"), str) or not isinstance(tip.get("message"), str) or not isinstance(tip.get("severity"), str):
                return _error("INVALID_MODEL_OUTPUT", "Invalid tip shape", details={"tip": tip}, status_code=502)

        analysis = model_json.get("analysis")
        if analysis is not None and not isinstance(analysis, dict):
            return _error("INVALID_MODEL_OUTPUT", "Invalid analysis", details={"analysis": analysis}, status_code=502)

        return {"ok": True, "score": score, "tips": tips, "analysis": analysis}
    except RuntimeError as e:
        code = e.args[0] if len(e.args) > 0 else "OLLAMA_ERROR"
        details = e.args[1] if len(e.args) > 1 else None
        return _error(
            str(code),
            "Ollama request failed",
            details=details,
            status_code=502,
        )
    except Exception as e:
        return _error("INTERNAL_ERROR", "Internal error", details=str(e), status_code=500)


@router.post("/parse")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    """
    Parse a resume file and return normalized data.
    
    Accepts: PDF, DOC, DOCX files via multipart/form-data
    Returns: JSON with normalized resume data
    """
    # Validate file extension
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "error": {
                    "code": "UNSUPPORTED_FILE_TYPE",
                    "message": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
                }
            }
        )
    
    # Save uploaded file to temporary location
    temp_path = None
    try:
        # Read file content to check size
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"File size exceeds maximum of {MAX_FILE_SIZE / (1024 * 1024):.0f}MB"
                    }
                }
            )
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Parse resume
        try:
            try:
                # Imported lazily so the API can run in Docker without bundling ../backend
                from backend.src.pipeline.parser import parse_resume  # type: ignore
                from backend.src.pipeline.normalizer import normalize_extracted_data  # type: ignore
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={
                        "ok": False,
                        "error": {
                            "code": "PIPELINE_UNAVAILABLE",
                            "message": "Resume parsing pipeline is not available in this environment",
                            "details": str(e),
                        },
                    },
                )

            raw_data = parse_resume(temp_path)
            normalized_data = normalize_extracted_data(raw_data)

            score, tips = _compute_score_and_tips_from_normalized_resume(normalized_data)
            
            return {
                "ok": True,
                "data": normalized_data,
                "score": {"value": score, "max": MAX_SCORE},
                "tips": tips,
            }
        except FileNotFoundError as e:
            return JSONResponse(
                status_code=404,
                content={
                    "ok": False,
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": str(e)
                    }
                }
            )
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "code": "PARSING_FAILED",
                        "message": str(e)
                    }
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": f"Internal error: {str(e)}"
                    }
                }
            )
    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass

