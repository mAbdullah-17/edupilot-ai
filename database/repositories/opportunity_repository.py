"""Data-access functions for opportunities, requirements, and saved opportunities."""

from database.database import get_db


# ── Opportunity queries ─────────────────────────────────

def get_opportunities(status: str = "active") -> list[dict]:
    """Return all opportunities with the given status, ordered by deadline."""
    return get_db().execute(
        "SELECT * FROM opportunities WHERE status = %s "
        "ORDER BY deadline ASC",
        (status,), fetch=True,
    ) or []


def get_opportunity_by_id(opp_id: int) -> dict | None:
    rows = get_db().execute(
        "SELECT * FROM opportunities WHERE id = %s", (opp_id,), fetch=True,
    )
    return rows[0] if rows else None


def search_opportunities(query: str, status: str = "active") -> list[dict]:
    """Full-text-ish search across title, organization, category, type, location."""
    like = f"%{query}%"
    return get_db().execute(
        "SELECT * FROM opportunities "
        "WHERE status = %s AND ("
        "  title LIKE %s OR organization LIKE %s OR category LIKE %s "
        "  OR opportunity_type LIKE %s OR location LIKE %s OR city LIKE %s "
        "  OR province LIKE %s OR country LIKE %s"
        ") ORDER BY deadline ASC",
        (status, like, like, like, like, like, like, like, like),
        fetch=True,
    ) or []


def filter_opportunities(
    category: str = None,
    opportunity_type: str = None,
    location: str = None,
    status: str = "active",
) -> list[dict]:
    """Filter opportunities by optional criteria using dynamic WHERE clauses."""
    clauses = ["status = %s"]
    params: list = [status]

    if category:
        clauses.append("category = %s")
        params.append(category)
    if opportunity_type:
        clauses.append("opportunity_type = %s")
        params.append(opportunity_type)
    if location:
        like_loc = f"%{location}%"
        clauses.append(
            "(city LIKE %s OR province LIKE %s OR country LIKE %s "
            "OR region LIKE %s OR location LIKE %s)"
        )
        params.extend([like_loc] * 5)

    where = " AND ".join(clauses)
    return get_db().execute(
        f"SELECT * FROM opportunities WHERE {where} ORDER BY deadline ASC",
        tuple(params), fetch=True,
    ) or []


def get_opportunities_with_location_priority(
    city: str = None,
    province: str = None,
    country: str = None,
    status: str = "active",
) -> list[dict]:
    """Return all active opportunities ordered by location proximity to user profile."""
    # Priority: city match > province > country > region > remote/international > rest
    priority_case = (
        "CASE "
        "  WHEN o.city = %s THEN 1 "
        "  WHEN o.province = %s THEN 2 "
        "  WHEN o.country = %s THEN 3 "
        "  WHEN o.region IS NOT NULL AND o.region != '' THEN 4 "
        "  WHEN o.location LIKE %s OR o.location LIKE %s THEN 5 "
        "  ELSE 6 "
        "END"
    )
    remote_like = "%remote%"
    intl_like = "%international%"
    params = (city, province, country, remote_like, intl_like, status)

    return get_db().execute(
        f"SELECT o.*, {priority_case} AS location_priority "
        "FROM opportunities o "
        "WHERE o.status = %s "
        "ORDER BY location_priority ASC, o.deadline ASC",
        params, fetch=True,
    ) or []


def get_distinct_categories() -> list[str]:
    rows = get_db().execute(
        "SELECT DISTINCT category FROM opportunities "
        "WHERE status = 'active' ORDER BY category",
        fetch=True,
    )
    return [r["category"] for r in rows] if rows else []


def get_distinct_types() -> list[str]:
    rows = get_db().execute(
        "SELECT DISTINCT opportunity_type FROM opportunities "
        "WHERE status = 'active' ORDER BY opportunity_type",
        fetch=True,
    )
    return [r["opportunity_type"] for r in rows] if rows else []


def count_opportunities(status: str = "active") -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM opportunities WHERE status = %s",
        (status,), fetch=True,
    )
    return rows[0]["cnt"] if rows else 0


def find_existing_opportunity(title: str, organization: str, external_url: str = "") -> dict | None:
    """Find a matching opportunity without changing existing data."""
    rows = get_db().execute(
        "SELECT id, title, organization, external_url FROM opportunities "
        "WHERE (LOWER(title) = LOWER(%s) AND LOWER(organization) = LOWER(%s)) "
        "   OR (external_url IS NOT NULL AND external_url = %s) LIMIT 1",
        (title, organization, external_url), fetch=True,
    )
    return rows[0] if rows else None


def insert_discovered_opportunity(data: dict) -> int:
    """Insert a live-discovered opportunity. Existing rows are never updated."""
    return get_db().execute(
        "INSERT INTO opportunities "
        "(title, organization, description, category, opportunity_type, "
        "location, city, province, country, region, deadline, external_url, "
        "eligibility_summary, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'active')",
        (
            data.get("title"), data.get("organization"), data.get("description"),
            data.get("category"), data.get("opportunity_type"), data.get("location"),
            data.get("city"), data.get("province"), data.get("country"),
            data.get("region"), data.get("deadline"), data.get("external_url"),
            data.get("eligibility_summary"),
        ),
    )

def insert_requirement(opportunity_id: int, requirement_type: str, description: str) -> int:
    return get_db().execute(
        "INSERT INTO opportunity_requirements "
        "(opportunity_id, requirement_type, description) VALUES (%s,%s,%s)",
        (opportunity_id, requirement_type, description),
    )


# ── Opportunity requirements ────────────────────────────

def get_requirements_by_opportunity_id(opp_id: int) -> list[dict]:
    return get_db().execute(
        "SELECT * FROM opportunity_requirements "
        "WHERE opportunity_id = %s ORDER BY id",
        (opp_id,), fetch=True,
    ) or []


# ── Saved opportunities ─────────────────────────────────

def save_opportunity(user_id: int, opp_id: int):
    """Save an opportunity for a user. Ignores duplicates."""
    get_db().execute(
        "INSERT IGNORE INTO saved_opportunities (user_id, opportunity_id) "
        "VALUES (%s, %s)",
        (user_id, opp_id),
    )


def unsave_opportunity(user_id: int, opp_id: int):
    """Remove a saved opportunity for a user."""
    get_db().execute(
        "DELETE FROM saved_opportunities "
        "WHERE user_id = %s AND opportunity_id = %s",
        (user_id, opp_id),
    )


def is_opportunity_saved(user_id: int, opp_id: int) -> bool:
    rows = get_db().execute(
        "SELECT 1 FROM saved_opportunities "
        "WHERE user_id = %s AND opportunity_id = %s",
        (user_id, opp_id), fetch=True,
    )
    return bool(rows)


def get_saved_opportunities(user_id: int) -> list[dict]:
    return get_db().execute(
        "SELECT o.* FROM opportunities o "
        "INNER JOIN saved_opportunities so ON so.opportunity_id = o.id "
        "WHERE so.user_id = %s ORDER BY so.saved_at DESC",
        (user_id,), fetch=True,
    ) or []
