"""Day 5 data-access functions — Notifications, Audit Logs, Admin."""

from database.database import get_db


# ── Notifications ────────────────────────────────────────

def create_notification(user_id: int, title: str, message: str,
                        notif_type: str = "info") -> int:
    """Insert a notification for a user. Returns insert id."""
    return get_db().execute(
        "INSERT INTO notifications (user_id, title, message, notif_type) "
        "VALUES (%s, %s, %s, %s)",
        (user_id, title, message, notif_type),
    )


def get_user_notifications(user_id: int, limit: int = 50) -> list[dict]:
    """Return notifications for a user, newest first."""
    return get_db().execute(
        "SELECT * FROM notifications WHERE user_id = %s "
        "ORDER BY created_at DESC LIMIT %s",
        (user_id, limit), fetch=True,
    ) or []


def get_unread_count(user_id: int) -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM notifications "
        "WHERE user_id = %s AND is_read = FALSE",
        (user_id,), fetch=True,
    )
    return rows[0]["cnt"] if rows else 0


def mark_notification_read(notif_id: int, user_id: int):
    """Mark a single notification read (user_id guard prevents cross-user access)."""
    get_db().execute(
        "UPDATE notifications SET is_read = TRUE "
        "WHERE id = %s AND user_id = %s",
        (notif_id, user_id),
    )


def mark_all_read(user_id: int):
    get_db().execute(
        "UPDATE notifications SET is_read = TRUE WHERE user_id = %s",
        (user_id,),
    )


def delete_notification(notif_id: int, user_id: int):
    get_db().execute(
        "DELETE FROM notifications WHERE id = %s AND user_id = %s",
        (notif_id, user_id),
    )


# ── Audit Logs ──────────────────────────────────────────

def log_action(actor_id: int, actor_email: str, action: str,
               entity_type: str = None, entity_id: int = None,
               details: str = None):
    """Record an admin audit-log entry."""
    get_db().execute(
        "INSERT INTO audit_logs "
        "(actor_id, actor_email, action, entity_type, entity_id, details) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (actor_id, actor_email, action, entity_type, entity_id, details),
    )


def get_audit_logs(limit: int = 100) -> list[dict]:
    return get_db().execute(
        "SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT %s",
        (limit,), fetch=True,
    ) or []


# ── Admin — User Management ─────────────────────────────

def get_all_users() -> list[dict]:
    """Return all users (id, full_name, email, role, is_active, created_at)."""
    return get_db().execute(
        "SELECT id, full_name, email, role, is_active, created_at "
        "FROM users ORDER BY created_at DESC",
        fetch=True,
    ) or []


def set_user_active(user_id: int, is_active: bool):
    get_db().execute(
        "UPDATE users SET is_active = %s WHERE id = %s",
        (is_active, user_id),
    )


def count_users() -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM users", fetch=True
    )
    return rows[0]["cnt"] if rows else 0


def count_active_students() -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM users "
        "WHERE role = 'STUDENT' AND is_active = TRUE",
        fetch=True,
    )
    return rows[0]["cnt"] if rows else 0


def count_total_applications() -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM applications", fetch=True
    )
    return rows[0]["cnt"] if rows else 0


def count_audit_logs() -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM audit_logs", fetch=True
    )
    return rows[0]["cnt"] if rows else 0


# ── Admin — Opportunity CRUD ────────────────────────────

def create_opportunity(data: dict) -> int:
    """Insert a new opportunity. Returns insert id."""
    return get_db().execute(
        "INSERT INTO opportunities "
        "(title, organization, description, category, opportunity_type, "
        " location, city, province, country, region, deadline, "
        " external_url, eligibility_summary, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            data.get("title"), data.get("organization"),
            data.get("description", ""), data.get("category"),
            data.get("opportunity_type"), data.get("location", ""),
            data.get("city", ""), data.get("province", ""),
            data.get("country", ""), data.get("region", ""),
            data.get("deadline") or None,
            data.get("external_url", ""),
            data.get("eligibility_summary", ""),
            data.get("status", "active"),
        ),
    )


def update_opportunity(opp_id: int, data: dict):
    """Update editable fields on an opportunity."""
    fields = ["title", "organization", "description", "category",
              "opportunity_type", "location", "city", "province",
              "country", "region", "deadline", "external_url",
              "eligibility_summary", "status"]
    updates = {k: data[k] for k in fields if k in data}
    if not updates:
        return
    set_clause = ", ".join(f"{col} = %s" for col in updates)
    values = list(updates.values()) + [opp_id]
    get_db().execute(
        f"UPDATE opportunities SET {set_clause} WHERE id = %s",
        tuple(values),
    )


def archive_opportunity(opp_id: int):
    get_db().execute(
        "UPDATE opportunities SET status = 'inactive' WHERE id = %s",
        (opp_id,),
    )


def get_all_opportunities_admin() -> list[dict]:
    """Return all opportunities regardless of status, for admin view."""
    return get_db().execute(
        "SELECT id, title, organization, category, opportunity_type, "
        "status, deadline, created_at FROM opportunities "
        "ORDER BY created_at DESC",
        fetch=True,
    ) or []
