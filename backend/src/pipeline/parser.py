"""Resume parser using PyResparser."""

from pyresparser import ResumeParser
from pathlib import Path


def parse_resume(file_path: str) -> dict:
    """
    Parse a resume file using PyResparser.
    
    Args:
        file_path: Path to the resume file (PDF, DOC, or DOCX)
        
    Returns:
        Dictionary with extracted resume data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If parsing fails or file format is unsupported
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    
    if not path.suffix.lower() in ['.pdf', '.doc', '.docx']:
        raise ValueError(f"Unsupported file format: {path.suffix}. Supported: .pdf, .doc, .docx")
    
    try:
        parser = ResumeParser(file_path)
        extracted_data = parser.get_extracted_data()
        
        if not extracted_data:
            raise ValueError("Failed to extract data from resume")
        
        return extracted_data
    except Exception as e:
        raise ValueError(f"Error parsing resume: {str(e)}") from e

