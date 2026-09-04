"""Profile service — save/skip sections, completion calculation."""

from database.repositories import profile_repository as repo


# ── Profile field groups ──────────────────────────────

PERSONAL_FIELDS = [
    "date_of_birth",
    "nationality",
    "country",
    "province",
    "city",
]

EDUCATION_FIELDS = [
    "education_level",
    "current_institution",
    "current_field",
    "current_cgpa",
]

# Contact / Professional fields — kept unchanged.
CONTACT_FIELDS = [
    "phone",
    "linkedin_url",
    "github_url",
    "website",
]

EXPERIENCE_FIELDS = [
    "experience",
]

SKILLS_FIELDS = [
    "skills",
]

CAREER_FIELDS = [
    "career_preferences",
]


PROFILE_SECTIONS = {
    "personal": PERSONAL_FIELDS,
    "education": EDUCATION_FIELDS,
    "contact": CONTACT_FIELDS,
    "experience": EXPERIENCE_FIELDS,
    "skills": SKILLS_FIELDS,
    "career": CAREER_FIELDS,
}


# ── Completion weights ────────────────────────────────

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


def calculate_completion(
    user_id: int,
    completed_sections: set[str]
) -> int:
    """Calculate and persist profile completion percentage."""

    total = sum(
        _SECTION_WEIGHTS.get(section, 0)
        for section in completed_sections
    )

    total = min(total, 100)

    repo.update_profile_completion(user_id, total)

    # Keep Streamlit session state synchronized.
    try:
        import streamlit as st
        st.session_state["_last_completion"] = total
    except Exception:
        pass

    return total


def get_profile(user_id: int) -> dict | None:
    """Return the user's profile."""
    return repo.find_profile_by_user_id(user_id)


# ── User preferences ─────────────────────────────────


def get_user_preferences(user_id: int) -> dict:
    """Return user preferences, creating defaults if needed."""

    prefs = repo.get_user_preferences(user_id)

    if not prefs:
        from database.repositories.auth_repository import (
            create_default_preferences
        )

        create_default_preferences(user_id)
        prefs = repo.get_user_preferences(user_id)

    return prefs or {}


def save_user_preferences(user_id: int, data: dict):
    """Persist user preference settings."""

    allowed = [
        "notification_enabled",
        "email_enabled",
        "preferred_language",
        "preferred_location",
    ]

    fields = {
        key: value
        for key, value in data.items()
        if key in allowed
    }

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

        for field in PERSONAL_FIELDS:
            value = profile.get(field)

            if value not in (None, ""):
                personal[
                    field.replace("_", " ").title()
                ] = str(value)

        if personal:
            sections["personal"] = personal

        education = {}

        for field in EDUCATION_FIELDS:
            value = profile.get(field)

            if value not in (None, ""):
                education[
                    field.replace("_", " ").title()
                ] = str(value)

        if education:
            sections["education"] = education

        # Contact / Professional section kept unchanged.
        contact = {}

        for field in CONTACT_FIELDS:
            value = profile.get(field)

            if value not in (None, ""):
                contact[
                    field.replace("_", " ").title()
                ] = str(value)

        if contact:
            sections["contact"] = contact

        experience = profile.get("experience")

        if experience not in (None, ""):
            sections["experience"] = {
                "Experience": str(experience)
            }

        skills = profile.get("skills")

        if skills not in (None, ""):
            sections["skills"] = {
                "Skills": str(skills)
            }

        career_preferences = profile.get(
            "career_preferences"
        )

        if career_preferences not in (None, ""):
            sections["career"] = {
                "Career Preferences": str(career_preferences)
            }

        sections["completion"] = profile.get(
            "profile_completion",
            0
        )

    if prefs:
        sections["preferences"] = {
            "Notifications":
                "Enabled"
                if prefs.get("notification_enabled")
                else "Disabled",

            "Email Alerts":
                "Enabled"
                if prefs.get("email_enabled")
                else "Disabled",

            "Language":
                prefs.get("preferred_language", "en"),

            "Location":
                prefs.get("preferred_location", "—") or "—",
        }

    return sections