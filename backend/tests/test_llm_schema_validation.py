import pytest
from pydantic import ValidationError

from backend.src.llm.schema import validate_analyze_result


def test_valid_json_passes():
    data = {
        "score": 500,
        "tips": [{"id": "skills", "message": "Add more", "severity": "WARNING"}],
        "analysis": {"foo": "bar"},
    }
    result = validate_analyze_result(data)
    assert result.score == 500
    assert result.tips[0].severity == "WARNING"


def test_invalid_score_fails():
    data = {"score": 2000, "tips": [{"id": "x", "message": "y", "severity": "GOOD"}], "analysis": {}}
    with pytest.raises(ValidationError):
        validate_analyze_result(data)


def test_missing_fields_fail():
    data = {"score": 10}
    with pytest.raises(ValidationError):
        validate_analyze_result(data)


