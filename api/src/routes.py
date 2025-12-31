"""API routes for resume parsing."""

import tempfile
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from backend.src.pipeline.parser import parse_resume
from backend.src.pipeline.normalizer import normalize_extracted_data

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


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

