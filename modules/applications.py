"""Application tracking service — apply, list, status management (Day 3).

Pages call this module. This module calls the repository.
No SQL in pages.
"""

from database.repositories import application_repository as repo
from modules import opportunities as opp_svc


def apply_to_opportunity(user_id: int, opp_id: int) -> dict:
    """Create a new application. Returns {success: bool, message: str}."""
    existing = repo.get_application(user_id, opp_id)
    if existing:
        return {"success": False, "message": "You have already applied to this opportunity."}

    opp = opp_svc.get_opportunity(opp_id)
    if not opp:
        return {"success": False, "message": "Opportunity not found."}

    app_id = repo.create_application(user_id, opp_id)
    if app_id:
        return {"success": True, "message": "Application submitted successfully."}
    return {"success": False, "message": "Failed to submit application. Please try again."}


def get_my_applications(user_id: int) -> list[dict]:
    """Return all applications for a user with opportunity details."""
    return repo.get_applications_by_user(user_id)


def get_application_status(user_id: int, opp_id: int) -> dict | None:
    """Check if user has applied to an opportunity. Returns application row or None."""
    return repo.get_application(user_id, opp_id)


def get_application_counts(user_id: int) -> dict:
    """Return status counts for My Applications tabs.

    Returns: {"all": int, "applied": int, "in_review": int, "shortlisted": int, "rejected": int}
    """
    counts = repo.count_applications_by_status(user_id)
    total = sum(counts.values())
    return {
        "all": total,
        "applied": counts.get("applied", 0),
        "in_review": counts.get("in_review", 0),
        "shortlisted": counts.get("shortlisted", 0),
        "rejected": counts.get("rejected", 0),
    }
