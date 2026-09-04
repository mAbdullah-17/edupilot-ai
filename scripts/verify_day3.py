"""Quick Day 3 verification script."""
from database.database import get_db

db = get_db()

students = db.execute(
    "SELECT id, email, full_name, role FROM users WHERE role = 'STUDENT' LIMIT 5",
    fetch=True,
)
print("=== STUDENTS ===")
for s in students:
    print(s)

print("\n=== OPPORTUNITIES ===")
opps = db.execute("SELECT COUNT(*) AS cnt FROM opportunities", fetch=True)
print(f"Total: {opps[0]['cnt']}")

print("\n=== PROFILES ===")
profs = db.execute(
    "SELECT user_id, nationality, education_level, date_of_birth, "
    "current_cgpa, profile_completion FROM profiles LIMIT 5",
    fetch=True,
)
for p in profs:
    print(p)

print("\n=== APPLICATIONS TABLE ===")
try:
    apps = db.execute("SELECT COUNT(*) AS cnt FROM applications", fetch=True)
    print(f"Total applications: {apps[0]['cnt']}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== REQUIREMENTS ===")
reqs = db.execute(
    "SELECT opportunity_id, requirement_type, description "
    "FROM opportunity_requirements LIMIT 10",
    fetch=True,
)
for r in reqs:
    print(r)
