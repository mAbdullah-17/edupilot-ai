"""Eligibility analysis engine — rule-based profile-vs-requirements matching.

Compares a student's profile data against an opportunity's requirements
and returns a per-requirement breakdown with three-state results:
Eligible / Not Eligible / Cannot Determine.

No AI / no external API calls — pure Python logic.
"""

import re
from datetime import date, datetime
from modules.profile import get_profile
from modules import opportunities as opp_svc

_FAR_FUTURE = date(9999, 12, 31)


def _sort_deadline(d) -> date:
    """Return a date for sorting; None deadlines sort last."""
    if d is None:
        return _FAR_FUTURE
    if hasattr(d, "date"):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return _FAR_FUTURE
    return _FAR_FUTURE


# ── Education level hierarchy (low → high) ────────────────
_EDU_RANK = {
    "intermediate": 1, "hssc": 1, "a-levels": 1, "a-level": 1,
    "diploma": 2,
    "bachelor": 3, "bachelors": 3, "undergraduate": 3, "bs": 3,
    "master": 4, "masters": 4, "ms": 4, "ma": 4, "mphil": 4,
    "phd": 5, "doctorate": 5, "doctoral": 5,
}

_EDU_KEYWORDS = [
    "phd", "doctorate", "doctoral",
    "mphil", "master", "masters", "ms ", "ma ",
    "bachelor", "bachelors", "undergraduate", "bs ",
    "diploma",
    "intermediate", "hssc", "a-levels", "a-level",
]


def _edu_rank(level_str: str | None) -> int:
    """Return a numeric rank for an education level string (0 = unknown)."""
    if not level_str:
        return 0
    low = level_str.lower()
    for kw in _EDU_KEYWORDS:
        if kw in low:
            return _EDU_RANK.get(kw.strip(), 0)
    return 0


# ── Per-type matchers ──────────────────────────────────────

def _match_nationality(profile: dict, description: str) -> dict:
    """Check nationality requirement against profile."""
    nat = profile.get("nationality") or ""
    country = profile.get("country") or ""
    combined = f"{nat} {country}".lower().strip()

    if not combined:
        return {
            "status": "Cannot Determine",
            "user_value": "Not provided",
            "explanation": "Nationality not recorded in profile. "
                           "Please add it in Profile Setup > Personal Information.",
        }

    # Extract nationality keywords from description (words that look like nationalities/countries)
    desc_lower = description.lower()
    # Common nationality patterns
    nationality_words = [
        "pakistani", "indian", "bangladeshi", "american", "british",
        "european", "african", "asian", "chinese", "german", "french",
        "pakistan", "india", "bangladesh", "usa", "uk", "europe",
        "ajk",
    ]
    for word in nationality_words:
        if word in desc_lower:
            if word in combined:
                return {
                    "status": "Eligible",
                    "user_value": nat or country,
                    "explanation": f"Your nationality ({nat or country}) matches the requirement.",
                }
            else:
                return {
                    "status": "Not Eligible",
                    "user_value": nat or country,
                    "explanation": f"This opportunity requires {word.title()} nationality, "
                                   f"but your profile shows {nat or country}.",
                }

    # Generic fallback — can't parse
    return {
        "status": "Cannot Determine",
        "user_value": nat or country,
        "explanation": "Could not automatically verify nationality requirement. "
                       "Please check the requirement description manually.",
    }


def _match_academic(profile: dict, description: str) -> dict:
    """Check academic/education requirement against profile."""
    edu_level = profile.get("education_level") or ""
    cgpa = profile.get("current_cgpa")
    desc_lower = description.lower()

    user_parts = []
    if edu_level:
        user_parts.append(edu_level)
    if cgpa is not None:
        user_parts.append(f"CGPA {cgpa}")
    user_value = ", ".join(user_parts) if user_parts else "Not provided"

    if not edu_level:
        return {
            "status": "Cannot Determine",
            "user_value": "Not provided",
            "explanation": "Education level not recorded in profile. "
                           "Please complete Profile Setup > Education.",
        }

    # Check education level requirement
    req_rank = _edu_rank(description)
    user_rank = _edu_rank(edu_level)

    # Check CGPA requirement
    cgpa_match = re.search(r"(?:cgpa|gpa|marks?)[\s:]*(?:of|>=|above|at least)?\s*([\d.]+)", desc_lower)
    cgpa_req = None
    if cgpa_match:
        try:
            cgpa_req = float(cgpa_match.group(1))
        except ValueError:
            cgpa_req = None

    # Also check for percentage-style marks (e.g. "80%", "80 marks")
    pct_match = re.search(r"([\d.]+)\s*(?:%|percent|marks?)", desc_lower)
    pct_req = None
    if pct_match:
        try:
            pct_req = float(pct_match.group(1))
        except ValueError:
            pct_req = None

    # Evaluate education level
    level_ok = True
    if req_rank > 0 and user_rank > 0:
        level_ok = user_rank >= req_rank
    elif req_rank > 0 and user_rank == 0:
        level_ok = None  # can't determine

    # Evaluate CGPA
    cgpa_ok = True
    if cgpa_req is not None:
        if cgpa is not None:
            cgpa_ok = float(cgpa) >= cgpa_req
        else:
            cgpa_ok = None  # can't determine

    # Evaluate percentage (if present and CGPA not the main metric)
    pct_ok = True
    if pct_req is not None and cgpa_req is None:
        # This is a percentage-based requirement (e.g. "80% marks")
        # We can't directly compare percentage to CGPA, so mark as Cannot Determine
        # unless we have CGPA and can loosely convert
        if cgpa is not None:
            # Rough conversion: CGPA 4.0 scale → percentage (CGPA/4 * 100)
            approx_pct = (float(cgpa) / 4.0) * 100
            pct_ok = approx_pct >= pct_req
        else:
            pct_ok = None

    # Determine overall status
    checks = [level_ok, cgpa_ok, pct_ok]
    if False in checks:
        return {
            "status": "Not Eligible",
            "user_value": user_value,
            "explanation": _build_academic_not_eligible_msg(
                edu_level, cgpa, description, level_ok, cgpa_ok, cgpa_req, pct_ok, pct_req),
        }
    if None in checks:
        return {
            "status": "Cannot Determine",
            "user_value": user_value,
            "explanation": "Some academic criteria could not be automatically verified. "
                           "Please review the requirement description.",
        }
    return {
        "status": "Eligible",
        "user_value": user_value,
        "explanation": "Your education level and CGPA meet the requirement.",
    }


def _build_academic_not_eligible_msg(edu, cgpa, desc, level_ok, cgpa_ok, cgpa_req, pct_ok, pct_req):
    parts = []
    if level_ok is False:
        parts.append(f"Education level '{edu}' does not meet the required level")
    if cgpa_ok is False and cgpa_req:
        parts.append(f"CGPA {cgpa} is below the required {cgpa_req}")
    if pct_ok is False and pct_req:
        parts.append(f"Approximate percentage ({round(float(cgpa)/4*100, 1) if cgpa else 'N/A'}%) "
                      f"is below the required {pct_req}%")
    return ". ".join(parts) if parts else "Academic requirement not met."


def _match_age(profile: dict, description: str) -> dict:
    """Check age requirement against profile date_of_birth."""
    dob = profile.get("date_of_birth")
    if not dob:
        return {
            "status": "Cannot Determine",
            "user_value": "Not provided",
            "explanation": "Date of birth not recorded in profile. "
                           "Please add it in Profile Setup > Personal Information.",
        }

    # Parse max age from description
    age_match = re.search(r"(?:maximum|max|under|below|at most|less than|age)\s*(\d+)",
                          description.lower())
    if not age_match:
        # Try "XX years" pattern
        age_match = re.search(r"(\d+)\s*years", description.lower())

    if not age_match:
        return {
            "status": "Cannot Determine",
            "user_value": _format_dob(dob),
            "explanation": "Could not parse age requirement from the description.",
        }

    max_age = int(age_match.group(1))
    if hasattr(dob, "date"):
        dob = dob.date()
    if isinstance(dob, str):
        from datetime import datetime
        dob = datetime.strptime(dob, "%Y-%m-%d").date()

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age <= max_age:
        return {
            "status": "Eligible",
            "user_value": f"{age} years",
            "explanation": f"Your age ({age}) is within the maximum of {max_age} years.",
        }
    return {
        "status": "Not Eligible",
        "user_value": f"{age} years",
        "explanation": f"Your age ({age}) exceeds the maximum of {max_age} years.",
    }


def _format_dob(dob) -> str:
    if hasattr(dob, "strftime"):
        return dob.strftime("%d %b %Y")
    return str(dob)


def _match_cannot_determine(req_type: str, description: str) -> dict:
    """Generic handler for requirement types that have no profile data."""
    explanations = {
        "language": "Language proficiency is not recorded in your profile. "
                     "Please check the requirement manually.",
        "technical": "Technical skills are not recorded in your profile. "
                      "Please check the requirement manually.",
        "experience": "Work experience is not recorded in your profile yet. "
                       "Please check the requirement manually.",
        "test": "Standardised test scores are not recorded in your profile. "
                 "Please check the requirement manually.",
        "financial": "Financial information is not recorded in your profile. "
                      "Please check the requirement manually.",
        "commitment": "Please review this commitment requirement manually.",
    }
    return {
        "status": "Cannot Determine",
        "user_value": "Not provided",
        "explanation": explanations.get(req_type,
            "This requirement cannot be automatically verified from your profile."),
    }


# ── Main analysis function ────────────────────────────────

_MATCHERS = {
    "nationality": _match_nationality,
    "academic": _match_academic,
    "age": _match_age,
}


def analyze_eligibility(user_id: int, opp_id: int) -> dict:
    """Analyse a student's eligibility for an opportunity.

    Returns:
        {
            "overall": "Eligible" | "Not Eligible" | "Cannot Determine",
            "match_pct": int (0-100),
            "rows": [ {requirement, user_value, required, status, explanation}, ... ]
        }
    """
    requirements = opp_svc.get_requirements(opp_id)

    # ── Divide-by-zero guard ──
    if not requirements:
        return {"overall": "Cannot Determine", "match_pct": 0, "rows": []}

    profile = get_profile(user_id) or {}
    rows = []

    for req in requirements:
        req_type = (req.get("requirement_type") or "").lower().strip()
        description = req.get("description") or ""

        matcher = _MATCHERS.get(req_type)
        if matcher:
            result = matcher(profile, description)
        else:
            result = _match_cannot_determine(req_type, description)

        rows.append({
            "requirement": req_type.title(),
            "required": description,
            "user_value": result["user_value"],
            "status": result["status"],
            "explanation": result["explanation"],
        })

    # ── Overall status ──
    statuses = [r["status"] for r in rows]
    if "Not Eligible" in statuses:
        overall = "Not Eligible"
    elif all(s == "Eligible" for s in statuses):
        overall = "Eligible"
    else:
        overall = "Cannot Determine"

    eligible_count = sum(1 for s in statuses if s == "Eligible")
    match_pct = round((eligible_count / len(statuses)) * 100)

    return {"overall": overall, "match_pct": match_pct, "rows": rows}


# ── Bulk helpers for For Me / Relevant ────────────────────

def get_for_me_opportunities(user_id: int) -> list[dict]:
    """Return opportunities where the student is NOT ruled out.

    Includes Eligible and Cannot Determine (excludes Not Eligible).
    Sorted by match_pct descending, then deadline ascending.
    """
    all_opps = opp_svc.get_all_opportunities(user_id=user_id)
    results = []
    for opp in all_opps:
        analysis = analyze_eligibility(user_id, opp["id"])
        if analysis["overall"] != "Not Eligible" and analysis["match_pct"] >= 20:
            opp_copy = dict(opp)
            opp_copy["match_pct"] = analysis["match_pct"]
            opp_copy["eligibility_status"] = analysis["overall"]
            results.append(opp_copy)
    results.sort(key=lambda x: (-x["match_pct"], _sort_deadline(x.get("deadline"))))
    return results


def get_relevant_opportunities(user_id: int) -> list[dict]:
    """Return opportunities with any profile connection (match_pct > 0).

    Sorted by match_pct descending, then deadline ascending.
    """
    all_opps = opp_svc.get_all_opportunities(user_id=user_id)
    results = []
    for opp in all_opps:
        analysis = analyze_eligibility(user_id, opp["id"])
        if analysis["match_pct"] >= 20:
            opp_copy = dict(opp)
            opp_copy["match_pct"] = analysis["match_pct"]
            opp_copy["eligibility_status"] = analysis["overall"]
            results.append(opp_copy)
    results.sort(key=lambda x: (-x["match_pct"], _sort_deadline(x.get("deadline"))))
    return results
