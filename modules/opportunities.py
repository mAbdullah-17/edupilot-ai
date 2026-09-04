"""Opportunity discovery service — search, filter, location priority, save/unsave.

Pages call this module.  This module calls the repository.
No SQL in pages.
"""

from database.repositories import opportunity_repository as repo
from modules.profile import get_profile


# ── Retrieve opportunities ──────────────────────────────

def get_all_opportunities(user_id: int = None) -> list[dict]:
    """Return all active opportunities, optionally ordered by user's location."""
    if user_id:
        profile = get_profile(user_id)
        if profile:
            city = profile.get("city") or ""
            province = profile.get("province") or ""
            country = profile.get("country") or ""
            if city or province or country:
                return repo.get_opportunities_with_location_priority(
                    city=city, province=province, country=country,
                )
    return repo.get_opportunities()


def get_opportunity(opp_id: int) -> dict | None:
    return repo.get_opportunity_by_id(opp_id)


def get_requirements(opp_id: int) -> list[dict]:
    return repo.get_requirements_by_opportunity_id(opp_id)


def count_opportunities() -> int:
    return repo.count_opportunities()


# ── Search ──────────────────────────────────────────────

def search(query: str) -> list[dict]:
    """Search opportunities by keyword across key fields."""
    if not query or not query.strip():
        return repo.get_opportunities()
    return repo.search_opportunities(query.strip())


# ── Filter ──────────────────────────────────────────────

def filter_opportunities(
    category: str = None,
    opportunity_type: str = None,
    location: str = None,
) -> list[dict]:
    return repo.filter_opportunities(
        category=category,
        opportunity_type=opportunity_type,
        location=location,
    )


def get_filter_options() -> dict:
    """Return available categories and types for filter dropdowns."""
    return {
        "categories": repo.get_distinct_categories(),
        "types": repo.get_distinct_types(),
    }


# ── Save / Unsave ───────────────────────────────────────

def save_opportunity(user_id: int, opp_id: int):
    repo.save_opportunity(user_id, opp_id)


def unsave_opportunity(user_id: int, opp_id: int):
    repo.unsave_opportunity(user_id, opp_id)


def is_saved(user_id: int, opp_id: int) -> bool:
    return repo.is_opportunity_saved(user_id, opp_id)


def get_saved_opportunities(user_id: int) -> list[dict]:
    return repo.get_saved_opportunities(user_id)


# ── Formatting helpers ──────────────────────────────────

def format_deadline(deadline) -> str:
    """Return a human-friendly deadline string."""
    if not deadline:
        return "No deadline"
    from datetime import date
    if hasattr(deadline, "strftime"):
        return deadline.strftime("%d %b %Y")
    return str(deadline)


def days_until_deadline(deadline) -> int | None:
    """Return days remaining, or None if no deadline."""
    if not deadline:
        return None
    from datetime import date
    if hasattr(deadline, "date"):
        deadline = deadline.date()
    if isinstance(deadline, date):
        delta = (deadline - date.today()).days
        return delta
    return None


def get_location_label(opp: dict) -> str:
    """Build a concise location label from opportunity fields."""
    parts = []
    if opp.get("city"):
        parts.append(opp["city"])
    if opp.get("province"):
        parts.append(opp["province"])
    if opp.get("country"):
        parts.append(opp["country"])
    if not parts and opp.get("location"):
        return opp["location"]
    return ", ".join(parts) if parts else "Not specified"


# ── Live discovery ─────────────────────────────────────
def refresh_live_opportunities(user_id: int | None = None, limit: int = 8) -> dict:
    """Search current web opportunities with Groq GPT-OSS 120B browser search
    and add only new rows. Hard-capped at 8 results — see
    modules.opportunity_discovery.MAX_RESULTS, which enforces this
    regardless of what limit is passed here."""
    from modules.opportunity_discovery import discover, sync_to_database
    city = province = country = ""
    if user_id:
        profile = get_profile(user_id) or {}
        city = profile.get("city") or ""
        province = profile.get("province") or ""
        country = profile.get("country") or "Pakistan"
    else:
        country = "Pakistan"
    items = discover(city, province, country, limit=limit)
    inserted, skipped = sync_to_database(items)
    return {"found": len(items), "inserted": inserted, "skipped": skipped}
