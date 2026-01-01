"""
Resume scoring service (domain layer).

Deterministic: driven solely by normalized resume content.
No FastAPI / HTTP dependencies.
"""

from __future__ import annotations

import re

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

    def _strings_from(v) -> list[str]:
        """
        Best-effort extraction of strings from unknown JSON-ish structures.
        Deterministic and explainable: strings, lists/tuples/sets, and dict values.
        """
        if v is None:
            return []
        if isinstance(v, str):
            s = v.strip()
            return [s] if s else []
        if isinstance(v, (list, tuple, set)):
            out: list[str] = []
            for item in v:
                out.extend(_strings_from(item))
            return out
        if isinstance(v, dict):
            out: list[str] = []
            for item in v.values():
                out.extend(_strings_from(item))
            return out
        # Ignore non-text scalars (int/float/bool) on purpose.
        return []

    def _any_nonempty_text(keys: tuple[str, ...]) -> bool:
        for k in keys:
            if _strings_from(normalized_resume.get(k)):
                return True
        return False

    def _contains_quantified_impact(text: str) -> bool:
        """
        Simple, explainable heuristic: look for numbers and common impact indicators.
        Examples: %, $, €, k/M scale, years, users, requests/sec.
        """
        t = (text or "").strip()
        if not t:
            return False

        # Fast path: any digit at all.
        if re.search(r"\d", t):
            return True

        tl = t.lower()
        # Common symbols/units even if numbers were stripped/obscured.
        return any(
            token in tl
            for token in (
                "%",
                "$",
                "€",
                "£",
                "₹",
                "users",
                "requests/sec",
                "request/sec",
                "req/sec",
                "req/s",
                "rps",
                "years",
                "year",
                "yrs",
                "yr",
                "months",
                "month",
                "mos",
                "k ",
                " m ",
                "million",
                "billion",
            )
        )

    def _skills_look_grouped(skills: list[str]) -> bool:
        """
        Simple grouping heuristic: treat a skill entry as a "category line" if it
        looks like 'Category: item, item' or 'Category - item, item'.
        """
        if not skills:
            return False

        category_line = re.compile(r"^\s*[A-Za-z][A-Za-z &/]{2,25}\s*[:\-]\s*\S")
        common_labels = re.compile(
            r"^\s*(languages?|frameworks?|libraries?|tools?|databases?|cloud|platforms?|devops|testing|ml|ai)\s*[:\-]\s*\S",
            flags=re.IGNORECASE,
        )
        for s in skills:
            if category_line.search(s) or common_labels.search(s):
                return True
        return False

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

    # A) Quantified impact in work experience (simple heuristic)
    # Driven only by normalized_resume: scan common experience fields if provided.
    experience_exists = company_count > 0 or _any_nonempty_text(
        (
            "work_experience",
            "experience",
            "experience_text",
            "employment_history",
            "professional_experience",
        )
    )
    if experience_exists:
        experience_blobs: list[str] = []
        # Include these even if they're "metadata"—in many pipelines they contain
        # full lines or bullet-ish snippets.
        for k in (
            "work_experience",
            "experience",
            "experience_text",
            "employment_history",
            "professional_experience",
            "company_names",
            "designation",
        ):
            experience_blobs.extend(_strings_from(normalized_resume.get(k)))

        combined = "\n".join(experience_blobs)
        if _contains_quantified_impact(combined):
            tips.append(
                {
                    "id": "quantified_impact_good",
                    "message": "Your experience includes measurable impact (metrics, scale, or outcomes)",
                    "severity": "GOOD",
                }
            )
        else:
            tips.append(
                {
                    "id": "quantified_impact",
                    "message": "Add a few numbers to your experience bullets (%, $, scale, years, users, etc.)",
                    "severity": "WARNING",
                }
            )

    # C) Skills structure (simple heuristic)
    skills = normalized_resume.get("skills")
    if isinstance(skills, list) and all(isinstance(s, str) for s in skills):
        grouped = _skills_look_grouped([s.strip() for s in skills if s and s.strip()])
        if grouped:
            tips.append(
                {
                    "id": "skills_structure_good",
                    "message": "Nice touch: skills are organized into categories, which improves readability",
                    "severity": "GOOD",
                }
            )
        elif skills_count > 10:
            tips.append(
                {
                    "id": "skills_structure",
                    "message": "Consider grouping skills into categories (e.g., Languages, Frameworks, Tools) to make scanning easier",
                    "severity": "WARNING",
                }
            )

    # D) Education vs experience balance
    education_exists = degree_count > 0 or _count_list("college_name") > 0
    if experience_exists and not education_exists:
        tips.append(
            {
                "id": "education_experience_balance",
                "message": "Add an education section to balance your work experience (degree, school, or relevant coursework)",
                "severity": "WARNING",
            }
        )
    elif education_exists and not experience_exists:
        tips.append(
            {
                "id": "education_experience_balance",
                "message": "Add a work experience section to complement your education (internships, projects, or roles)",
                "severity": "WARNING",
            }
        )
    elif education_exists and experience_exists:
        tips.append(
            {
                "id": "education_experience_balance_good",
                "message": "Good balance: both education and work experience are included",
                "severity": "GOOD",
            }
        )

    # E) Professional summary / headline
    summary_present = _any_nonempty_text(
        ("summary", "professional_summary", "profile", "about", "headline", "objective")
    )
    if summary_present:
        tips.append(
            {
                "id": "summary_good",
                "message": "A professional summary helps recruiters understand your focus quickly",
                "severity": "GOOD",
            }
        )
    else:
        tips.append(
            {
                "id": "summary",
                "message": "Add a short professional summary or headline to set context at the top",
                "severity": "WARNING",
            }
        )

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


