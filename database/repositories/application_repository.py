"""Data-access functions for application tracking (Day 3)."""

from database.database import get_db


def create_application(user_id: int, opportunity_id: int) -> int | None:
    """Insert a new application. Returns insert_id or None if duplicate."""
    try:
        return get_db().execute(
            "INSERT IGNORE INTO applications (user_id, opportunity_id) "
            "VALUES (%s, %s)",
            (user_id, opportunity_id),
        )
    except Exception:
        return None


def get_application(user_id: int, opportunity_id: int) -> dict | None:
    """Return a single application row, or None."""
    rows = get_db().execute(
        "SELECT * FROM applications "
        "WHERE user_id = %s AND opportunity_id = %s",
        (user_id, opportunity_id),
        fetch=True,
    )
    return rows[0] if rows else None


def get_applications_by_user(user_id: int) -> list[dict]:
    """Return all applications for a user, joined with opportunity details."""
    return get_db().execute(
        "SELECT a.id AS application_id, a.status, a.applied_at, a.notes, "
        "       o.id, o.title, o.organization, o.category, "
        "       o.opportunity_type, o.location, o.city, o.province, "
        "       o.country, o.region, o.deadline, o.external_url "
        "FROM applications a "
        "INNER JOIN opportunities o ON o.id = a.opportunity_id "
        "WHERE a.user_id = %s "
        "ORDER BY a.applied_at DESC",
        (user_id,),
        fetch=True,
    ) or []


def update_application_status(app_id: int, status: str):
    """Update the status of an application."""
    get_db().execute(
        "UPDATE applications SET status = %s WHERE id = %s",
        (status, app_id),
    )


def count_applications_by_status(user_id: int) -> dict:
    """Return a dict of {status: count} for a user's applications."""
    rows = get_db().execute(
        "SELECT status, COUNT(*) AS cnt "
        "FROM applications WHERE user_id = %s GROUP BY status",
        (user_id,),
        fetch=True,
    ) or []
    return {r["status"]: r["cnt"] for r in rows}
