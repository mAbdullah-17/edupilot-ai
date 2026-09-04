"""Data-access functions for user authentication and password-reset tokens."""

from datetime import datetime
from database.database import get_db


# ── User queries ───────────────────────────────────────

def find_user_by_email(email: str) -> dict | None:
    rows = get_db().execute(
        "SELECT * FROM users WHERE email = %s", (email,), fetch=True
    )
    return rows[0] if rows else None


def find_user_by_id(user_id: int) -> dict | None:
    rows = get_db().execute(
        "SELECT * FROM users WHERE id = %s", (user_id,), fetch=True
    )
    return rows[0] if rows else None


def create_user(full_name: str, email: str, password_hash: str,
                role: str = "STUDENT") -> int:
    return get_db().execute(
        "INSERT INTO users (full_name, email, password_hash, role) "
        "VALUES (%s, %s, %s, %s)",
        (full_name, email, password_hash, role),
    )


def count_users_by_email(email: str) -> int:
    rows = get_db().execute(
        "SELECT COUNT(*) AS cnt FROM users WHERE email = %s",
        (email,), fetch=True,
    )
    return rows[0]["cnt"] if rows else 0


def create_default_preferences(user_id: int):
    get_db().execute(
        "INSERT IGNORE INTO user_preferences (user_id) VALUES (%s)",
        (user_id,),
    )


# ── Password-reset token queries ──────────────────────

def store_reset_token(user_id: int, token_hash: str,
                      expires_at: datetime) -> int:
    return get_db().execute(
        "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) "
        "VALUES (%s, %s, %s)",
        (user_id, token_hash, expires_at),
    )


def find_valid_token(token_hash: str) -> dict | None:
    rows = get_db().execute(
        "SELECT * FROM password_reset_tokens "
        "WHERE token_hash = %s AND used_at IS NULL AND expires_at > NOW()",
        (token_hash,), fetch=True,
    )
    return rows[0] if rows else None


def mark_token_used(token_id: int):
    get_db().execute(
        "UPDATE password_reset_tokens SET used_at = NOW() WHERE id = %s",
        (token_id,),
    )


def update_user_password(user_id: int, password_hash: str):
    get_db().execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (password_hash, user_id),
    )
