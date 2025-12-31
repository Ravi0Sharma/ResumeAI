"""Resume parser extracting text from PDF/DOCX and deriving simple fields.

This module intentionally avoids PyResparser/spaCy (incompatible with Python 3.11 in many envs).
The output is a best-effort dict compatible with the normalizer.
"""

from __future__ import annotations

import re
from pathlib import Path

from pdfminer.high_level import extract_text  # type: ignore
from docx import Document  # type: ignore


def parse_resume(file_path: str) -> dict:
    """
    Parse a resume file by extracting text (PDF/DOCX) and deriving basic fields.
    
    Args:
        file_path: Path to the resume file (PDF or DOCX)
        
    Returns:
        Dictionary with extracted resume data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If parsing fails or file format is unsupported
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    try:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            text = (extract_text(str(path)) or "").strip()
        elif suffix == ".docx":
            doc = Document(str(path))
            text = "\n".join((p.text or "").strip() for p in doc.paragraphs if (p.text or "").strip()).strip()
        elif suffix == ".doc":
            raise ValueError("Unsupported file format: .doc. Supported: .pdf, .docx")
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Supported: .pdf, .docx")

        if not text:
            raise ValueError("Failed to extract text from resume")

        # Best-effort field derivation (deterministic, driven by extracted text).
        email_match = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, flags=re.IGNORECASE)
        phone_match = re.search(
            r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}",
            text,
        )

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        name = lines[0] if lines else None
        if name and (email_match and email_match.group(0) in name):
            name = None

        # Extract a "skills" section if present: take lines after "Skills" header until blank/header-ish.
        skills: list[str] = []
        for i, ln in enumerate(lines):
            if re.fullmatch(r"skills", ln, flags=re.IGNORECASE):
                for nxt in lines[i + 1 : i + 8]:
                    if re.fullmatch(r"[A-Z][A-Z\s]{2,}", nxt):  # next major header
                        break
                    parts = re.split(r"[,•|/]\s*", nxt)
                    skills.extend([p.strip() for p in parts if p.strip()])
                break

        # Very light heuristics for degree + company names.
        degree: list[str] = []
        for pat in (r"\bB\.?Sc\b", r"\bM\.?Sc\b", r"\bB\.?E\b", r"\bB\.?Tech\b", r"\bM\.?Tech\b", r"\bMBA\b", r"\bPh\.?D\b"):
            if re.search(pat, text, flags=re.IGNORECASE):
                degree.append(pat.replace(r"\b", "").replace("\\", "").replace("?", "").replace(".", ""))

        company_names: list[str] = []
        for ln in lines:
            if re.search(r"\b(Inc|LLC|Ltd|AB|GmbH|Company)\b", ln, flags=re.IGNORECASE):
                company_names.append(ln[:120])
            if len(company_names) >= 5:
                break

        extracted_data = {
            "name": name,
            "email": email_match.group(0) if email_match else None,
            "mobile_number": phone_match.group(0) if phone_match else None,
            "skills": skills,
            "total_experience": None,
            "degree": degree,
            "college_name": [],
            "designation": [],
            "company_names": company_names,
            "no_of_pages": None,
        }

        return extracted_data
    except Exception as e:
        raise ValueError(f"Error parsing resume: {str(e)}") from e


