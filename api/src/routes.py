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
            
            return {
                "ok": True,
                "data": normalized_data
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

