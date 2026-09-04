"""Check admin user and reset password if needed."""
import sys
sys.path.insert(0, ".")
from database.database import get_db
from modules.auth import hash_password

db = get_db()
rows = db.execute("SELECT id, email, full_name, role FROM users WHERE role = 'ADMIN'", fetch=True)
for r in (rows or []):
    print(r)

# Reset admin password to Test1234
if rows:
    admin_id = rows[0]["id"]
    new_hash = hash_password("Test1234")
    db.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, admin_id))
    print(f"Admin user {admin_id} password reset to: Test1234")
