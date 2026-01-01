"""API routes for resume parsing."""

import tempfile
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_SCORE = 1000


class AnalyzeRequest(BaseModel):
    cv_text: str
    job_text: str


def _error(code: str, message: str, *, details=None, status_code: int = 500) -> JSONResponse:
    payload = {"ok": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


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

    try:
        from backend.src.llm.analyze_service import DomainError, analyze  # type: ignore

        result = analyze(cv_text, job_text)
        return {
            "ok": True,
            "score": result.score,
            "tips": [t.model_dump() for t in result.tips],
            "analysis": result.analysis,
        }
    except DomainError as e:
        # Preserve previous contract: invalid JSON parse => code only (no message).
        if e.code == "INVALID_MODEL_OUTPUT" and e.message is None and e.details is None:
            return JSONResponse(
                status_code=502,
                content={"ok": False, "error": {"code": "INVALID_MODEL_OUTPUT"}},
            )
        return _error(str(e.code), e.message or "Invalid model output", details=e.details, status_code=502)
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
                from backend.src.resume.parse_service import parse  # type: ignore
                from backend.src.resume.score_service import score  # type: ignore
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

            normalized_data = parse(temp_path)
            score_value, tips = score(normalized_data)
            
            return {
                "ok": True,
                "data": normalized_data,
                "score": {"value": score_value, "max": MAX_SCORE},
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

