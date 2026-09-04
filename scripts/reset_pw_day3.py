"""Reset password for user 3 to 'Test1234' for browser verification."""
import sys
sys.path.insert(0, ".")
from database.database import get_db
from modules.auth import hash_password

db = get_db()
new_hash = hash_password("Test1234")
db.execute("UPDATE users SET password_hash = %s WHERE id = 3", (new_hash,))
print("Password for user 3 (day1_corr_test@example.com) reset to: Test1234")

# Verify
row = db.execute("SELECT id, email, full_name FROM users WHERE id = 3", fetch=True)
print(f"User: {row[0]}")
