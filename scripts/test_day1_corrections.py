"""Day 1 correction — integration test script."""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_db
from database.repositories import profile_repository as repo
from database.repositories.auth_repository import find_user_by_email
from modules.profile import (
    ensure_profile_exists, save_section, get_profile,
    calculate_completion, get_user_preferences, save_user_preferences,
    get_profile_view,
)
from modules.auth import register, login_student, login_admin, generate_reset_token, complete_password_reset

db = get_db()
passed = 0
failed = 0
manual = []
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS: {label}")
        passed += 1
    else:
        print(f"  FAIL: {label} — {detail}")
        failed += 1


# ── 1. Schema: new columns ────────────────────────────
print("\n=== 1. Schema: new columns in profiles ===")
cols = db.execute("SHOW COLUMNS FROM profiles", fetch=True)
col_names = [c["Field"] for c in cols]
for new_col in ["profile_image_path", "phone", "linkedin_url", "github_url", "website"]:
    check(f"Column '{new_col}' exists", new_col in col_names)

# ── 2. Registration ───────────────────────────────────
print("\n=== 2. Registration ===")
test_email = "day1_corr_test@example.com"
existing = find_user_by_email(test_email)
if existing:
    user_id = existing["id"]
    print(f"  Using existing test user id={user_id}")
else:
    result = register("Day1 Test User", test_email, "TestPass123!")
    check("Registration succeeds", result["ok"], result.get("message"))
    user_id = result["user_id"]

# Duplicate email
dup = register("Dup User", test_email, "AnotherPass1!")
check("Duplicate email rejected", not dup["ok"])

# ── 3. Login ──────────────────────────────────────────
print("\n=== 3. Student login ===")
login_result = login_student(test_email, "TestPass123!")
check("Student login succeeds", login_result["ok"], login_result.get("message"))
check("Student login returns user", login_result.get("user") is not None)

# Wrong password
bad_login = login_student(test_email, "WrongPassword1!")
check("Wrong password rejected", not bad_login["ok"])

# ── 4. Admin login ────────────────────────────────────
print("\n=== 4. Admin login ===")
from config import settings as cfg
admin_result = login_admin(cfg.ADMIN_EMAIL, cfg.ADMIN_PASSWORD)
check("Admin login succeeds", admin_result["ok"], admin_result.get("message"))

# Student can't login as admin
student_as_admin = login_admin(test_email, "TestPass123!")
check("Student rejected from admin login", not student_as_admin["ok"])

# ── 5. Profile save & load ────────────────────────────
print("\n=== 5. Profile save & load ===")
ensure_profile_exists(user_id)

save_section(user_id, "personal", {
    "nationality": "Pakistani", "country": "Pakistan",
    "province": "Sindh", "city": "Karachi",
})
save_section(user_id, "education", {
    "education_level": "Bachelor's",
    "current_institution": "NED University",
    "current_field": "Computer Science",
    "current_cgpa": 3.5,
})
save_section(user_id, "contact", {
    "phone": "03001234567",
    "linkedin_url": "https://linkedin.com/in/test",
    "github_url": "https://github.com/test",
    "website": "https://test.dev",
})

profile = get_profile(user_id)
check("Nationality saved", profile.get("nationality") == "Pakistani")
check("City saved", profile.get("city") == "Karachi")
check("Education level saved", profile.get("education_level") == "Bachelor's")
check("CGPA saved", float(profile.get("current_cgpa", 0)) == 3.5)
check("Phone saved", profile.get("phone") == "03001234567")
check("LinkedIn saved", profile.get("linkedin_url") == "https://linkedin.com/in/test")
check("GitHub saved", profile.get("github_url") == "https://github.com/test")
check("Website saved", profile.get("website") == "https://test.dev")

# Reload to verify persistence
profile2 = get_profile(user_id)
check("Data persists on reload", profile2.get("nationality") == "Pakistani")

# ── 6. Completion calculation ─────────────────────────
print("\n=== 6. Completion calculation ===")
pct = calculate_completion(user_id, {"personal", "education"})
check("Completion = 50% for personal+education", pct == 50, f"got {pct}")

pct2 = calculate_completion(user_id, {"personal", "education", "experience", "skills", "career"})
check("Completion = 100% for all sections", pct2 == 100, f"got {pct2}")

# ── 7. Preferences ────────────────────────────────────
print("\n=== 7. User preferences ===")
prefs = get_user_preferences(user_id)
check("Default preferences exist", prefs is not None and len(prefs) > 0)

save_user_preferences(user_id, {
    "notification_enabled": False,
    "email_enabled": True,
    "preferred_language": "ur",
    "preferred_location": "Karachi",
})
prefs2 = get_user_preferences(user_id)
check("Notification pref saved", prefs2.get("notification_enabled") == 0)
check("Language pref saved", prefs2.get("preferred_language") == "ur")
check("Location pref saved", prefs2.get("preferred_location") == "Karachi")

# ── 8. Profile view helper ────────────────────────────
print("\n=== 8. Profile view helper ===")
view = get_profile_view(user_id)
check("View has account section", "account" in view)
check("View has personal section", "personal" in view)
check("View has education section", "education" in view)
check("View has contact section", "contact" in view)

# ── 9. Password reset flow ────────────────────────────
print("\n=== 9. Password reset ===")
# Create a UNIQUE test user for password reset to avoid state issues
import secrets as _secrets
pw_test_email = f"pw_test_{_secrets.token_hex(4)}@example.com"
pw_reg = register("PW Test User", pw_test_email, "OriginalPass1!")
pw_uid = pw_reg["user_id"]

reset_result = generate_reset_token(pw_test_email)
check("Token generated", reset_result["ok"])
check("Token returned in dev mode", reset_result.get("token") is not None)

raw_token = reset_result["token"]
# Use the token
reset_pw = complete_password_reset(raw_token, "NewSecure456!")
check("Password reset succeeds", reset_pw["ok"], reset_pw.get("message"))

# Old password rejected
old_login = login_student(pw_test_email, "OriginalPass1!")
check("Old password rejected", not old_login["ok"])

# New password works
new_login = login_student(pw_test_email, "NewSecure456!")
check("New password accepted", new_login["ok"])

# Token single-use
reuse = complete_password_reset(raw_token, "AnotherNew789!")
check("Token cannot be reused", not reuse["ok"])

# ── 10. Token expiry (simulated) ──────────────────────
print("\n=== 10. Token expiry (simulated) ===")
import hashlib
from datetime import datetime, timedelta
expired_time = datetime.now() - timedelta(hours=2)
db.execute(
    "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) "
    "VALUES (%s, %s, %s)",
    (user_id, hashlib.sha256(b"expired_test").hexdigest(), expired_time),
)
expired_result = complete_password_reset("expired_test", "ShouldNotWork1!")
check("Expired token rejected", not expired_result["ok"])

# ── 11. Non-existent email reset ──────────────────────
print("\n=== 11. Non-existent email reset ===")
fake_reset = generate_reset_token("nonexistent@fake.com")
check("Generic message for unknown email", fake_reset["ok"])
check("No token returned for unknown email", fake_reset.get("token") is None)

# ── 12. No SQL in UI files ────────────────────────────
print("\n=== 12. No SQL in UI files ===")
ui_files = [
    "pages/Dashboard.py", "pages/Login.py", "pages/Registration.py",
    "pages/Profile_Setup.py", "pages/Settings.py",
]
for f in ui_files:
    path = os.path.join(PROJECT_ROOT, f)
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    has_sql = any(kw in content.upper() for kw in ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "ALTER "])
    check(f"No SQL in {f}", not has_sql)

# ── 13. No secrets committed ──────────────────────────
print("\n=== 13. Security checks ===")
gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
with open(gitignore_path, "r") as fh:
    gi = fh.read()
check(".env in .gitignore", ".env" in gi)
check("uploads/* in .gitignore", "uploads/*" in gi)

# ── Summary ───────────────────────────────────────────
print(f"\n{'='*50}")
print(f"RESULTS: {passed} passed, {failed} failed")
if manual:
    print("\nMANUAL TESTS REQUIRED:")
    for m in manual:
        print(f"  - {m}")
print(f"{'='*50}")

sys.exit(0 if failed == 0 else 1)
