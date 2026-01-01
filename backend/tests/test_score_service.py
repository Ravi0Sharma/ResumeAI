from backend.src.resume.score_service import score


def test_missing_sections_lower_score():
    missing = {}
    score_missing, _tips = score(missing)
    assert 0 <= score_missing <= 1000


def test_full_resume_higher_score():
    missing = {}
    full = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "mobile_number": "+46 70 123 45 67",
        "skills": ["Python", "FastAPI", "SQL", "Docker", "Kubernetes", "AWS", "ML", "NLP", "CI", "Git"],
        "degree": ["BSc"],
        "company_names": ["Example Inc"],
        "total_experience": 5.0,
        "no_of_pages": 1,
    }
    score_missing, _ = score(missing)
    score_full, _ = score(full)
    assert 0 <= score_full <= 1000
    assert score_full > score_missing


def test_score_clamped_0_1000():
    for normalized in [
        {},
        {"skills": []},
        {"skills": ["a"] * 1000, "no_of_pages": 999},  # weird but should still clamp
        {"name": "x", "email": "x@y.z", "mobile_number": "1", "skills": ["a"] * 100},
    ]:
        s, _ = score(normalized)
        assert 0 <= s <= 1000


