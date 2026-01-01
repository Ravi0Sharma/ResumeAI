import pytest

from backend.src.llm import analyze_service


def test_analyze_service_returns_validated_output(monkeypatch):
    def fake_generate(_prompt: str) -> str:
        return '{"score": 123, "tips": [{"id":"x","message":"y","severity":"GOOD"}], "analysis": {"a": 1}}'

    monkeypatch.setattr(analyze_service.ollama_client, "generate", fake_generate)
    result = analyze_service.analyze("cv", "job")
    assert result.score == 123
    assert result.tips[0].id == "x"
    assert result.analysis == {"a": 1}


def test_analyze_service_invalid_json_raises_domain_error(monkeypatch):
    def fake_generate(_prompt: str) -> str:
        return "not json"

    monkeypatch.setattr(analyze_service.ollama_client, "generate", fake_generate)
    with pytest.raises(analyze_service.DomainError) as e:
        analyze_service.analyze("cv", "job")
    assert e.value.code == "INVALID_MODEL_OUTPUT"


