from backend.src.resume.score_service import score


def _tip_by_id(tips: list[dict], tip_id: str) -> dict | None:
    for t in tips:
        if t.get("id") == tip_id:
            return t
    return None


def test_quantified_impact_good_when_metrics_present():
    normalized = {
        "company_names": ["Acme Inc"],
        "experience_text": "Increased throughput by 30% and saved $50k while supporting 2M users.",
        "skills": ["Python", "SQL", "Docker", "AWS", "CI"],
        "degree": ["BSc"],
        "no_of_pages": 1,
    }
    _score, tips = score(normalized)
    tip = _tip_by_id(tips, "quantified_impact_good")
    assert tip is not None
    assert tip["severity"] == "GOOD"


def test_quantified_impact_warning_when_no_metrics():
    normalized = {
        "company_names": ["Acme Inc"],
        "experience_text": "Improved performance and reliability across core services.",
        "skills": ["Python", "SQL", "Docker", "AWS", "CI"],
        "degree": ["BSc"],
        "no_of_pages": 1,
    }
    _score, tips = score(normalized)
    tip = _tip_by_id(tips, "quantified_impact")
    assert tip is not None
    assert tip["severity"] == "WARNING"


def test_skills_structure_warning_when_flat_and_long():
    normalized = {
        "skills": [
            "Python",
            "Java",
            "JavaScript",
            "TypeScript",
            "React",
            "FastAPI",
            "SQL",
            "PostgreSQL",
            "Docker",
            "Kubernetes",
            "AWS",
        ],
        "degree": ["BSc"],
        "company_names": ["Example Inc"],
        "no_of_pages": 1,
    }
    _score, tips = score(normalized)
    tip = _tip_by_id(tips, "skills_structure")
    assert tip is not None
    assert tip["severity"] == "WARNING"


def test_skills_structure_good_when_grouped():
    normalized = {
        "skills": [
            "Languages: Python, Java",
            "Frameworks: FastAPI, React",
            "Tools - Docker, Git",
        ],
        "degree": ["BSc"],
        "company_names": ["Example Inc"],
        "no_of_pages": 1,
    }
    _score, tips = score(normalized)
    tip = _tip_by_id(tips, "skills_structure_good")
    assert tip is not None
    assert tip["severity"] == "GOOD"


def test_education_vs_experience_balance():
    # Experience but no education
    normalized_1 = {"company_names": ["Example Inc"], "degree": [], "skills": ["Python", "SQL", "Docker", "AWS", "CI"]}
    _score_1, tips_1 = score(normalized_1)
    tip_1 = _tip_by_id(tips_1, "education_experience_balance")
    assert tip_1 is not None
    assert tip_1["severity"] == "WARNING"

    # Education but no experience
    normalized_2 = {"company_names": [], "degree": ["BSc"], "skills": ["Python", "SQL", "Docker", "AWS", "CI"]}
    _score_2, tips_2 = score(normalized_2)
    tip_2 = _tip_by_id(tips_2, "education_experience_balance")
    assert tip_2 is not None
    assert tip_2["severity"] == "WARNING"

    # Both
    normalized_3 = {"company_names": ["Example Inc"], "degree": ["BSc"], "skills": ["Python", "SQL", "Docker", "AWS", "CI"]}
    _score_3, tips_3 = score(normalized_3)
    tip_3 = _tip_by_id(tips_3, "education_experience_balance_good")
    assert tip_3 is not None
    assert tip_3["severity"] == "GOOD"


def test_professional_summary_tip():
    normalized_with = {
        "summary": "Backend engineer focused on reliability and performance.",
        "skills": ["Python", "SQL", "Docker", "AWS", "CI"],
        "degree": ["BSc"],
        "company_names": ["Example Inc"],
    }
    _score_with, tips_with = score(normalized_with)
    tip_with = _tip_by_id(tips_with, "summary_good")
    assert tip_with is not None
    assert tip_with["severity"] == "GOOD"

    normalized_missing = {
        "skills": ["Python", "SQL", "Docker", "AWS", "CI"],
        "degree": ["BSc"],
        "company_names": ["Example Inc"],
    }
    _score_missing, tips_missing = score(normalized_missing)
    tip_missing = _tip_by_id(tips_missing, "summary")
    assert tip_missing is not None
    assert tip_missing["severity"] == "WARNING"


