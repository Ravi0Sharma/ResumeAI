"""
Resume parsing service (domain layer).

Transport layers (FastAPI, CLI, etc.) should call parse(file_path) and handle
I/O / error mapping externally.
"""

from __future__ import annotations


def parse(file_path: str) -> dict:
    """
    Parse a resume file and return normalized resume data.

    Args:
        file_path: Path to the resume file (PDF/DOC/DOCX)

    Returns:
        Normalized resume dict (stable keys)
    """
    # Kept as a local import so the service remains importable even if optional
    # parsing dependencies are not present in some environments.
    from backend.src.pipeline.parser import parse_resume  # type: ignore
    from backend.src.pipeline.normalizer import normalize_extracted_data  # type: ignore

    raw = parse_resume(file_path)
    return normalize_extracted_data(raw)


