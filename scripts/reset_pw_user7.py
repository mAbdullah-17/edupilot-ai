"""Reset password for user 7 to 'Test1234' for empty-profile testing."""
import sys
sys.path.insert(0, ".")
from database.database import get_db
from modules.auth import hash_password

db = get_db()
new_hash = hash_password("Test1234")
db.execute("UPDATE users SET password_hash = %s WHERE id = 7", (new_hash,))
print("Password for user 7 (test@test.com) reset to: Test1234")
