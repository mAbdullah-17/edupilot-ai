"""Profile service — save/skip sections, completion calculation."""

from database.repositories import profile_repository as repo

# ── Profile field groups ──────────────────────────────
# Each group maps to a set of columns in the profiles table.
# Used by Profile Setup to save sections independently.

PERSONAL_FIELDS = [
    "date_of_birth", "nationality", "country", "province", "city",
]

EDUCATION_FIELDS = [
    "education_level", "current_institution", "current_field", "current_cgpa",
]

CONTACT_FIELDS = [
    "phone", "linkedin_url", "github_url", "website",
]

# Experience, Skills, and Career Preferences will use their own
# dedicated tables on Day 2+. For Day 1, we track completion via
# session state flags and the profile_completion percentage.

PROFILE_SECTIONS = {
    "personal": PERSONAL_FIELDS,
    "education": EDUCATION_FIELDS,
    "contact": CONTACT_FIELDS,
    "experience": [],   # dedicated table — Day 2+
    "skills": [],       # dedicated table — Day 2+
    "career": [],       # dedicated table — Day 2+
}

# Weight of each section toward 100% completion
_SECTION_WEIGHTS = {
    "personal": 25,
    "education": 25,
    "experience": 20,
    "skills": 15,
    "career": 15,
}


def ensure_profile_exists(user_id: int):
    """Create a blank profile row if one does not exist."""
    if repo.find_profile_by_user_id(user_id) is None:
        repo.create_profile(user_id)


def save_section(user_id: int, section: str, data: dict):
    """Persist fields for a single profile section."""
    ensure_profile_exists(user_id)
    fields_to_save = {}
    allowed = PROFILE_SECTIONS.get(section, [])
    for key in allowed:
        if key in data and data[key] not in (None, ""):
            fields_to_save[key] = data[key]
    if fields_to_save:
        repo.update_profile_fields(user_id, fields_to_save)


def calculate_completion(user_id: int, completed_sections: set[str]) -> int:
    """Calculate and persist profile completion %.

    completed_sections is a set of section names the user has filled in.
    """
    total = sum(
        _SECTION_WEIGHTS.get(s, 0) for s in completed_sections
    )
    total = min(total, 100)
    repo.update_profile_completion(user_id, total)
    return total


def get_profile(user_id: int) -> dict | None:
    return repo.find_profile_by_user_id(user_id)



# ── User preferences ─────────────────────────────────

def get_user_preferences(user_id: int) -> dict:
    """Return user preferences, creating defaults if needed."""
    prefs = repo.get_user_preferences(user_id)
    if not prefs:
        from database.repositories.auth_repository import create_default_preferences
        create_default_preferences(user_id)
        prefs = repo.get_user_preferences(user_id)
    return prefs or {}


def save_user_preferences(user_id: int, data: dict):
    """Persist user preference settings."""
    allowed = ["notification_enabled", "email_enabled",
               "preferred_language", "preferred_location"]
    fields = {k: v for k, v in data.items() if k in allowed}
    if fields:
        repo.update_user_preferences(user_id, fields)


# ── Profile view helper ──────────────────────────────

def get_profile_view(user_id: int) -> dict:
    """Build a structured profile view for read-only display."""
    from database.repositories.auth_repository import find_user_by_id

    user = find_user_by_id(user_id)
    profile = get_profile(user_id)
    prefs = get_user_preferences(user_id)

    sections = {}

    if user:
        sections["account"] = {
            "Full Name": user.get("full_name", "—"),
            "Email": user.get("email", "—"),
            "Role": user.get("role", "—"),
        }

    if profile:
        personal = {}
        for f in PERSONAL_FIELDS:
            val = profile.get(f)
            if val not in (None, ""):
                personal[f.replace("_", " ").title()] = str(val)
        if personal:
            sections["personal"] = personal

        education = {}
        for f in EDUCATION_FIELDS:
            val = profile.get(f)
            if val not in (None, ""):
                education[f.replace("_", " ").title()] = str(val)
        if education:
            sections["education"] = education

        contact = {}
        for f in CONTACT_FIELDS:
            val = profile.get(f)
            if val not in (None, ""):
                contact[f.replace("_", " ").title()] = str(val)
        if contact:
            sections["contact"] = contact

        sections["completion"] = profile.get("profile_completion", 0)

    if prefs:
        sections["preferences"] = {
            "Notifications": "Enabled" if prefs.get("notification_enabled") else "Disabled",
            "Email Alerts": "Enabled" if prefs.get("email_enabled") else "Disabled",
            "Language": prefs.get("preferred_language", "en"),
            "Location": prefs.get("preferred_location", "—") or "—",
        }

    return sections
