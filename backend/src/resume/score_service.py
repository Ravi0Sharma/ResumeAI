"""
Resume scoring service (domain layer).

Deterministic: driven solely by normalized resume content.
No FastAPI / HTTP dependencies.
"""

from __future__ import annotations

MAX_SCORE = 1000


def score(normalized_resume: dict) -> tuple[int, list[dict]]:
    """
    Deterministically compute score + tips from parsed resume content.

    This MUST be driven only by extracted resume data (no mocks/randomness).
    """

    def _count_list(key: str) -> int:
        v = normalized_resume.get(key)
        if isinstance(v, list):
            return len([x for x in v if isinstance(x, str) and x.strip()])
        return 0

    def _has_str(key: str) -> bool:
        v = normalized_resume.get(key)
        return isinstance(v, str) and bool(v.strip())

    tips: list[dict] = []

    # Presence checks
    if not _has_str("name"):
        tips.append({"id": "name", "message": "Missing name", "severity": "NEEDS_WORK"})
    else:
        tips.append({"id": "name_good", "message": "Clear name provided", "severity": "GOOD"})
    if not _has_str("email"):
        tips.append({"id": "email", "message": "Missing email", "severity": "NEEDS_WORK"})
    else:
        tips.append({"id": "email_good", "message": "Professional email included", "severity": "GOOD"})
    if not _has_str("mobile_number"):
        tips.append({"id": "mobile_number", "message": "Phone number is missing", "severity": "NEEDS_WORK"})
    else:
        tips.append({"id": "mobile_number_good", "message": "Phone number detected", "severity": "GOOD"})

    skills_count = _count_list("skills")
    if skills_count < 5:
        tips.append(
            {
                "id": "skills",
                "message": f"Low skills coverage (found {skills_count})",
                "severity": "WARNING" if skills_count >= 3 else "NEEDS_WORK",
            }
        )
    else:
        tips.append(
            {
                "id": "skills_good",
                "message": f"Strong skills section ({skills_count} skills listed)",
                "severity": "GOOD",
            }
        )

    degree_count = _count_list("degree")
    if degree_count == 0:
        tips.append({"id": "education", "message": "Education not detected", "severity": "WARNING"})
    else:
        tips.append({"id": "education_good", "message": "Education section included", "severity": "GOOD"})

    company_count = _count_list("company_names")
    if company_count == 0:
        tips.append({"id": "experience", "message": "Work experience not detected", "severity": "WARNING"})
    else:
        tips.append({"id": "experience_good", "message": "Relevant work experience included", "severity": "GOOD"})

    total_experience = normalized_resume.get("total_experience")
    if total_experience is None:
        tips.append({"id": "total_experience", "message": "Total years of experience not specified", "severity": "WARNING"})
    else:
        tips.append({"id": "total_experience_good", "message": "Total experience detected", "severity": "GOOD"})

    pages = normalized_resume.get("no_of_pages")
    if isinstance(pages, int) and pages > 2:
        tips.append({"id": "length", "message": f"Resume is {pages} pages (consider shortening)", "severity": "WARNING"})
    elif isinstance(pages, int) and pages <= 2:
        tips.append({"id": "length_good", "message": f"Resume length looks good ({pages} pages)", "severity": "GOOD"})

    # Score is computed from field completeness + skills density.
    weights = {
        "name": 1.0,
        "email": 1.0,
        "mobile_number": 1.0,
        "skills": 2.0,
        "education": 1.0,
        "experience": 1.0,
        "total_experience": 1.0,
        "length": 0.5,
    }

    earned = 0.0
    possible = sum(weights.values())

    earned += weights["name"] if _has_str("name") else 0.0
    earned += weights["email"] if _has_str("email") else 0.0
    earned += weights["mobile_number"] if _has_str("mobile_number") else 0.0

    earned += weights["education"] if degree_count > 0 else 0.0
    earned += weights["experience"] if company_count > 0 else 0.0
    earned += weights["total_experience"] if total_experience is not None else 0.0

    # Skills: scale up to 10 skills, then cap.
    earned += weights["skills"] * min(1.0, skills_count / 10.0)

    # Length: 1.0 if <=2 pages, 0.5 if unknown, 0.0 if >2 pages.
    if isinstance(pages, int):
        earned += weights["length"] if pages <= 2 else 0.0
    else:
        earned += weights["length"] * 0.5

    computed_score = int(round(MAX_SCORE * (earned / possible))) if possible > 0 else 0
    computed_score = max(0, min(MAX_SCORE, computed_score))

    return computed_score, tips


