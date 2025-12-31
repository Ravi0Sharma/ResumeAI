"""Normalize extracted resume data to a stable schema."""


def normalize_extracted_data(data: dict) -> dict:
    """
    Normalize extracted resume data to a stable schema.
    
    Args:
        data: Raw extracted data from PyResparser
        
    Returns:
        Normalized dictionary with stable keys:
        - name: str | None
        - email: str | None
        - mobile_number: str | None
        - skills: list[str]
        - total_experience: float | None
        - degree: list[str]
        - college_name: list[str]
        - designation: list[str]
        - company_names: list[str]
        - no_of_pages: int | None
    """
    def to_list(value):
        """Convert value to list, handling strings and None."""
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
        return [str(value).strip()] if str(value).strip() else []
    
    def to_string(value):
        """Convert value to string or None."""
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip() if value.strip() else None
        return str(value).strip() if str(value).strip() else None
    
    def to_float(value):
        """Convert value to float or None."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def to_int(value):
        """Convert value to int or None."""
        if value is None:
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def normalize_skills(skills):
        """Normalize skills list: dedupe, strip, keep order."""
        if not skills:
            return []
        
        seen = set()
        result = []
        for skill in to_list(skills):
            skill_lower = skill.lower().strip()
            if skill_lower and skill_lower not in seen:
                seen.add(skill_lower)
                result.append(skill)
        
        return result
    
    # Extract and normalize fields
    normalized = {
        "name": to_string(data.get("name")),
        "email": to_string(data.get("email")),
        "mobile_number": to_string(data.get("mobile_number")),
        "skills": normalize_skills(data.get("skills")),
        "total_experience": to_float(data.get("total_experience")),
        "degree": to_list(data.get("degree")),
        "college_name": to_list(data.get("college_name")),
        "designation": to_list(data.get("designation")),
        "company_names": to_list(data.get("company_names")),
        "no_of_pages": to_int(data.get("no_of_pages")),
    }
    
    return normalized

