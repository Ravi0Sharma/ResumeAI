"""Tests for the normalizer module."""

import pytest
from ..normalizer import normalize_extracted_data


def test_normalize_empty_data():
    """Test normalization with empty data."""
    result = normalize_extracted_data({})
    
    assert result["name"] is None
    assert result["email"] is None
    assert result["mobile_number"] is None
    assert result["skills"] == []
    assert result["total_experience"] is None
    assert result["degree"] == []
    assert result["college_name"] == []
    assert result["designation"] == []
    assert result["company_names"] == []
    assert result["no_of_pages"] is None


def test_normalize_string_to_list():
    """Test that string values are converted to lists."""
    data = {
        "degree": "Bachelor of Science",
        "college_name": "MIT",
        "designation": "Software Engineer",
        "company_names": "Google"
    }
    
    result = normalize_extracted_data(data)
    
    assert result["degree"] == ["Bachelor of Science"]
    assert result["college_name"] == ["MIT"]
    assert result["designation"] == ["Software Engineer"]
    assert result["company_names"] == ["Google"]


def test_normalize_skills_deduplication():
    """Test that skills are deduplicated and trimmed."""
    data = {
        "skills": ["Python", "python", "JavaScript", "  Python  ", "Java"]
    }
    
    result = normalize_extracted_data(data)
    
    # Should dedupe and keep order
    assert len(result["skills"]) == 3
    assert "Python" in result["skills"]
    assert "JavaScript" in result["skills"]
    assert "Java" in result["skills"]


def test_normalize_skills_order():
    """Test that skills order is preserved."""
    data = {
        "skills": ["A", "B", "C"]
    }
    
    result = normalize_extracted_data(data)
    assert result["skills"] == ["A", "B", "C"]


def test_normalize_experience_types():
    """Test that experience is converted to float."""
    data = {"total_experience": "5.5"}
    result = normalize_extracted_data(data)
    assert result["total_experience"] == 5.5
    assert isinstance(result["total_experience"], float)
    
    data = {"total_experience": 10}
    result = normalize_extracted_data(data)
    assert result["total_experience"] == 10.0


def test_normalize_pages():
    """Test that pages are converted to int."""
    data = {"no_of_pages": "2"}
    result = normalize_extracted_data(data)
    assert result["no_of_pages"] == 2
    assert isinstance(result["no_of_pages"], int)
    
    data = {"no_of_pages": 3.7}
    result = normalize_extracted_data(data)
    assert result["no_of_pages"] == 3


def test_normalize_types_exact():
    """Test that all types are exactly as specified."""
    data = {
        "name": "John Doe",
        "email": "john@example.com",
        "mobile_number": "1234567890",
        "skills": ["Python", "JavaScript"],
        "total_experience": 5.5,
        "degree": ["BS"],
        "college_name": ["MIT"],
        "designation": ["Engineer"],
        "company_names": ["Google"],
        "no_of_pages": 2
    }
    
    result = normalize_extracted_data(data)
    
    assert isinstance(result["name"], str)
    assert isinstance(result["email"], str)
    assert isinstance(result["mobile_number"], str)
    assert isinstance(result["skills"], list)
    assert all(isinstance(s, str) for s in result["skills"])
    assert isinstance(result["total_experience"], float)
    assert isinstance(result["degree"], list)
    assert all(isinstance(d, str) for d in result["degree"])
    assert isinstance(result["college_name"], list)
    assert isinstance(result["designation"], list)
    assert isinstance(result["company_names"], list)
    assert isinstance(result["no_of_pages"], int)

