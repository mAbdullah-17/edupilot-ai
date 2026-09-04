"""Authentication service — registration, login, logout, admin bootstrap, password reset."""

import hashlib
import secrets
import time
from datetime import datetime, timedelta

import bcrypt

from config import settings
from database.repositories import auth_repository as repo

# ── Rate-limiting (in-memory) ─────────────────────────

_login_attempts: dict[str, list[float]] = {}
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 300  # 5 minutes


def _is_rate_limited(email: str) -> bool:
    now = time.time()
    attempts = _login_attempts.get(email, [])
    attempts = [t for t in attempts if now - t < _WINDOW_SECONDS]
    _login_attempts[email] = attempts
    return len(attempts) >= _MAX_ATTEMPTS


def _record_attempt(email: str):
    _login_attempts.setdefault(email, []).append(time.time())


def _clear_attempts(email: str):
    _login_attempts.pop(email, None)


# ── Password hashing ──────────────────────────────────

def hash_password(plaintext: str) -> str:
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))


# ── Registration ──────────────────────────────────────

def register(full_name: str, email: str, password: str) -> dict:
    """Register a new student. Returns {'ok': bool, 'message': str, 'user_id': int|None}."""
    email = email.strip().lower()

    if not full_name or not email or not password:
        return {"ok": False, "message": "All fields are required.", "user_id": None}

    if len(password) < 8:
        return {"ok": False, "message": "Password must be at least 8 characters.", "user_id": None}

    if repo.count_users_by_email(email) > 0:
        return {"ok": False, "message": "An account with this email already exists.", "user_id": None}

    pw_hash = hash_password(password)
    user_id = repo.create_user(full_name.strip(), email, pw_hash, role="STUDENT")
    repo.create_default_preferences(user_id)

    return {"ok": True, "message": "Account created successfully.", "user_id": user_id}


# ── Login ─────────────────────────────────────────────

def login_student(email: str, password: str) -> dict:
    """Authenticate a student. Returns {'ok': bool, 'message': str, 'user': dict|None}."""
    email = email.strip().lower()

    if _is_rate_limited(email):
        return {"ok": False, "message": "Too many attempts. Please wait a few minutes.", "user": None}

    user = repo.find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        _record_attempt(email)
        return {"ok": False, "message": "Invalid email or password.", "user": None}

    if user["role"] != "STUDENT":
        return {"ok": False, "message": "Invalid email or password.", "user": None}

    if not user["is_active"]:
        return {"ok": False, "message": "This account has been deactivated.", "user": None}

    _clear_attempts(email)
    return {"ok": True, "message": "Login successful.", "user": user}


def login_admin(email: str, password: str) -> dict:
    """Authenticate the configured administrator safely.

    The .env admin credentials are the bootstrap credentials for the demo.
    Existing admin rows are also accepted when their stored bcrypt hash matches
    the submitted password. This avoids a stale database hash preventing login
    after the configured admin password is changed.
    """
    email = email.strip().lower()

    if _is_rate_limited(email):
        return {"ok": False, "message": "Too many attempts. Please wait a few minutes.", "user": None}

    configured_email = settings.ADMIN_EMAIL.strip().lower()
    user = repo.find_user_by_email(email)

    # First, validate the configured bootstrap credentials. If the matching
    # admin exists, synchronize its password hash so .env remains authoritative
    # for this local/demo installation.
    if email == configured_email and secrets.compare_digest(password, settings.ADMIN_PASSWORD):
        if user and user.get("role") == "ADMIN":
            try:
                if not verify_password(password, user["password_hash"]):
                    repo.update_user_password(user["id"], hash_password(password))
                    user = repo.find_user_by_email(email) or user
            except (ValueError, TypeError):
                repo.update_user_password(user["id"], hash_password(password))
                user = repo.find_user_by_email(email) or user
        elif not user:
            pw_hash = hash_password(settings.ADMIN_PASSWORD)
            user_id = repo.create_user("Administrator", configured_email, pw_hash, role="ADMIN")
            repo.create_default_preferences(user_id)
            user = repo.find_user_by_id(user_id)
        else:
            # Do not silently convert an existing student account into an admin.
            _record_attempt(email)
            return {"ok": False, "message": "Invalid credentials.", "user": None}

        _clear_attempts(email)
        return {"ok": True, "message": "Admin login successful.", "user": user}

    if not user or user.get("role") != "ADMIN":
        _record_attempt(email)
        return {"ok": False, "message": "Invalid credentials.", "user": None}

    try:
        valid = verify_password(password, user["password_hash"])
    except (ValueError, TypeError):
        valid = False
    if not valid:
        _record_attempt(email)
        return {"ok": False, "message": "Invalid credentials.", "user": None}

    if not user["is_active"]:
        return {"ok": False, "message": "This account has been deactivated.", "user": None}

    _clear_attempts(email)
    return {"ok": True, "message": "Admin login successful.", "user": user}


# ── Admin bootstrap ───────────────────────────────────

def bootstrap_admin():
    """Ensure the configured admin account exists and its password is current."""
    email = settings.ADMIN_EMAIL.strip().lower()
    user = repo.find_user_by_email(email)

    if user:
        # Never change a non-admin account into an admin automatically.
        if user.get("role") != "ADMIN":
            return
        try:
            if not verify_password(settings.ADMIN_PASSWORD, user["password_hash"]):
                repo.update_user_password(user["id"], hash_password(settings.ADMIN_PASSWORD))
        except (ValueError, TypeError):
            repo.update_user_password(user["id"], hash_password(settings.ADMIN_PASSWORD))
        repo.create_default_preferences(user["id"])
        return

    pw_hash = hash_password(settings.ADMIN_PASSWORD)
    user_id = repo.create_user("Administrator", email, pw_hash, role="ADMIN")
    repo.create_default_preferences(user_id)


# ── Password reset ────────────────────────────────────

def generate_reset_token(email: str) -> dict:
    """Generate a reset token for the given email.

    Returns {'ok': bool, 'token': str|None, 'message': str}.
    The raw token is returned ONLY for the dev/demo simulated flow.
    It is never logged or stored anywhere.
    """
    email = email.strip().lower()
    user = repo.find_user_by_email(email)

    # Always return success to avoid account enumeration
    if not user:
        return {"ok": True, "token": None, "message": "If that email is registered, a reset link has been sent."}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now() + timedelta(hours=1)

    repo.store_reset_token(user["id"], token_hash, expires_at)

    return {"ok": True, "token": raw_token, "message": "If that email is registered, a reset link has been sent."}


def complete_password_reset(token: str, new_password: str) -> dict:
    """Validate token and set new password.

    Returns {'ok': bool, 'message': str}.
    """
    if not token or not new_password:
        return {"ok": False, "message": "Token and new password are required."}

    if len(new_password) < 8:
        return {"ok": False, "message": "Password must be at least 8 characters."}

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    token_row = repo.find_valid_token(token_hash)

    if not token_row:
        return {"ok": False, "message": "This reset link is invalid or has expired."}

    pw_hash = hash_password(new_password)
    repo.update_user_password(token_row["user_id"], pw_hash)
    repo.mark_token_used(token_row["id"])

    return {"ok": True, "message": "Password has been reset successfully. You can now log in."}
