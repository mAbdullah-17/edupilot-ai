"""Data-access functions for user profiles."""

from database.database import get_db


def find_profile_by_user_id(user_id: int) -> dict | None:
    rows = get_db().execute(
        "SELECT * FROM profiles WHERE user_id = %s",
        (user_id,),
        fetch=True,
    )

    return rows[0] if rows else None


def create_profile(user_id: int) -> int:
    return get_db().execute(
        "INSERT IGNORE INTO profiles (user_id) VALUES (%s)",
        (user_id,),
    )


def update_profile_fields(user_id: int, fields: dict):
    """Update only the supplied fields on the profile row."""

    if not fields:
        return

    set_clause = ", ".join(
        f"{column} = %s"
        for column in fields
    )

    values = list(fields.values()) + [user_id]

    get_db().execute(
        f"""
        UPDATE profiles
        SET {set_clause}
        WHERE user_id = %s
        """,
        tuple(values),
    )


def update_profile_completion(
    user_id: int,
    completion: int
):
    get_db().execute(
        """
        UPDATE profiles
        SET profile_completion = %s
        WHERE user_id = %s
        """,
        (completion, user_id),
    )


def get_profile_completion(user_id: int) -> int:
    rows = get_db().execute(
        """
        SELECT profile_completion
        FROM profiles
        WHERE user_id = %s
        """,
        (user_id,),
        fetch=True,
    )

    if rows:
        return rows[0]["profile_completion"]

    return 0


# ── User preferences queries ─────────────────────────


def get_user_preferences(user_id: int) -> dict | None:
    rows = get_db().execute(
        """
        SELECT *
        FROM user_preferences
        WHERE user_id = %s
        """,
        (user_id,),
        fetch=True,
    )

    return rows[0] if rows else None


def update_user_preferences(
    user_id: int,
    fields: dict
):
    """Update user preference fields."""

    if not fields:
        return

    set_clause = ", ".join(
        f"{column} = %s"
        for column in fields
    )

    values = list(fields.values()) + [user_id]

    get_db().execute(
        f"""
        UPDATE user_preferences
        SET {set_clause}
        WHERE user_id = %s
        """,
        tuple(values),
    )