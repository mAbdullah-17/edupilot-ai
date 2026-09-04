"""MySQL connection manager and database initialisation."""

import mysql.connector
from mysql.connector import pooling, Error as MySQLError
from config import settings


class Database:
    """Thin wrapper around a MySQL connection pool."""

    def __init__(self):
        self._pool = pooling.MySQLConnectionPool(
            pool_name="edupilot_pool",
            pool_size=5,
            pool_reset_session=True,
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=True,
        )

    # ── connection helpers ─────────────────────────────
    def get_connection(self):
        """Borrow a connection from the pool."""
        return self._pool.get_connection()

    def execute(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a single statement and optionally return rows."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.lastrowid
        except MySQLError:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def execute_many(self, query: str, params_list: list):
        """Execute a statement against a list of parameter tuples."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except MySQLError:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()


# ── bootstrap helpers ──────────────────────────────────

def ensure_database_exists():
    """Create the database if it does not yet exist."""
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        charset="utf8mb4",
    )
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` "
        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()
    conn.close()


def run_schema(db: Database):
    """Execute schema.sql to create tables if they don't exist."""
    with open(settings.SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()

    conn = db.get_connection()
    try:
        cursor = conn.cursor()
        for chunk in sql.split(";"):
            # Strip comment lines (--) before checking if there is a real statement
            lines = [
                line for line in chunk.splitlines()
                if not line.strip().startswith("--")
            ]
            statement = "\n".join(lines).strip()
            if statement:
                cursor.execute(statement)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ── Day 1 corrections migration ──────────────────────

def _add_column_if_not_exists(db: Database, table: str, column: str,
                              col_type: str):
    """Add a column to a table if it doesn't already exist."""
    try:
        db.execute(
            f"ALTER TABLE `{table}` ADD COLUMN `{column}` {col_type}",
        )
    except MySQLError:
        pass  # Column already exists — expected


def _migrate_day1_corrections(db: Database):
    """Add columns introduced in the Day 1 correction pass."""
    # Profile image path
    _add_column_if_not_exists(
        db, "profiles", "profile_image_path", "VARCHAR(500) DEFAULT NULL")
    # Contact / professional info
    _add_column_if_not_exists(
        db, "profiles", "phone", "VARCHAR(30) DEFAULT NULL")
    _add_column_if_not_exists(
        db, "profiles", "linkedin_url", "VARCHAR(500) DEFAULT NULL")
    _add_column_if_not_exists(
        db, "profiles", "github_url", "VARCHAR(500) DEFAULT NULL")
    _add_column_if_not_exists(
        db, "profiles", "website", "VARCHAR(500) DEFAULT NULL")


def _migrate_day3(db: Database):
    """Ensure Day 3 applications table exists (schema.sql already has it,
    but this is a safe belt-and-braces check)."""
    try:
        db.execute(
            "CREATE TABLE IF NOT EXISTS applications ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  opportunity_id INT NOT NULL,"
            "  status ENUM('applied','in_review','shortlisted','rejected')"
            "         NOT NULL DEFAULT 'applied',"
            "  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            "             ON UPDATE CURRENT_TIMESTAMP,"
            "  notes TEXT DEFAULT NULL,"
            "  UNIQUE KEY uq_user_app (user_id, opportunity_id),"
            "  INDEX idx_app_user (user_id),"
            "  INDEX idx_app_status (status)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        )
    except MySQLError:
        pass  # Table already exists — expected


def _migrate_day4(db: Database):
    """Ensure Day 4 AI student tool tables exist."""
    tables = {
        "chat_sessions": (
            "CREATE TABLE IF NOT EXISTS chat_sessions ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  title VARCHAR(255) DEFAULT 'New Chat',"
            "  context_type VARCHAR(50) NOT NULL DEFAULT 'General',"
            "  context_id INT DEFAULT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            "    ON UPDATE CURRENT_TIMESTAMP,"
            "  INDEX idx_chat_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "chat_messages": (
            "CREATE TABLE IF NOT EXISTS chat_messages ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  session_id INT NOT NULL,"
            "  role ENUM('user','assistant') NOT NULL,"
            "  content TEXT NOT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_chatmsg_session (session_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "study_materials": (
            "CREATE TABLE IF NOT EXISTS study_materials ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  filename VARCHAR(255) NOT NULL,"
            "  file_type VARCHAR(50) DEFAULT NULL,"
            "  file_path VARCHAR(500) DEFAULT NULL,"
            "  uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_study_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "study_results": (
            "CREATE TABLE IF NOT EXISTS study_results ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  material_id INT NOT NULL,"
            "  user_id INT NOT NULL,"
            "  result_type VARCHAR(50) NOT NULL,"
            "  content LONGTEXT NOT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_studyres_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "study_plans": (
            "CREATE TABLE IF NOT EXISTS study_plans ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  title VARCHAR(255) NOT NULL,"
            "  subject VARCHAR(255) DEFAULT NULL,"
            "  exam_date DATE DEFAULT NULL,"
            "  available_hours INT DEFAULT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"
            "    ON UPDATE CURRENT_TIMESTAMP,"
            "  INDEX idx_studyplan_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "study_tasks": (
            "CREATE TABLE IF NOT EXISTS study_tasks ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  plan_id INT NOT NULL,"
            "  title VARCHAR(255) NOT NULL,"
            "  description TEXT DEFAULT NULL,"
            "  due_date DATE DEFAULT NULL,"
            "  is_completed BOOLEAN NOT NULL DEFAULT FALSE,"
            "  week_number INT DEFAULT NULL,"
            "  day_of_week VARCHAR(20) DEFAULT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_studytask_plan (plan_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "career_recommendations": (
            "CREATE TABLE IF NOT EXISTS career_recommendations ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  career_title VARCHAR(255) NOT NULL,"
            "  match_score INT DEFAULT NULL,"
            "  explanation TEXT DEFAULT NULL,"
            "  skill_gaps TEXT DEFAULT NULL,"
            "  roadmap TEXT DEFAULT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_career_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "resume_analyses": (
            "CREATE TABLE IF NOT EXISTS resume_analyses ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  filename VARCHAR(255) DEFAULT NULL,"
            "  target_role VARCHAR(255) DEFAULT NULL,"
            "  strengths TEXT DEFAULT NULL,"
            "  weaknesses TEXT DEFAULT NULL,"
            "  detected_skills TEXT DEFAULT NULL,"
            "  missing_keywords TEXT DEFAULT NULL,"
            "  ats_score INT DEFAULT NULL,"
            "  ats_notes TEXT DEFAULT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_resume_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "interview_sessions": (
            "CREATE TABLE IF NOT EXISTS interview_sessions ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  role_title VARCHAR(255) NOT NULL,"
            "  difficulty VARCHAR(50) NOT NULL DEFAULT 'Beginner',"
            "  interview_type VARCHAR(50) NOT NULL DEFAULT 'Mixed',"
            "  status VARCHAR(20) NOT NULL DEFAULT 'active',"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  finished_at TIMESTAMP NULL DEFAULT NULL,"
            "  INDEX idx_interview_user (user_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "interview_questions": (
            "CREATE TABLE IF NOT EXISTS interview_questions ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  session_id INT NOT NULL,"
            "  question TEXT NOT NULL,"
            "  user_answer TEXT DEFAULT NULL,"
            "  feedback TEXT DEFAULT NULL,"
            "  question_order INT NOT NULL DEFAULT 0,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_intq_session (session_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
    }
    for _name, ddl in tables.items():
        try:
            db.execute(ddl)
        except MySQLError:
            pass  # Table already exists — expected


def _migrate_day5(db: Database):
    """Create Day 5 tables (notifications, audit_logs) if they don't exist."""
    tables = {
        "notifications": (
            "CREATE TABLE IF NOT EXISTS notifications ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  user_id INT NOT NULL,"
            "  title VARCHAR(255) NOT NULL,"
            "  message TEXT NOT NULL,"
            "  notif_type VARCHAR(50) NOT NULL DEFAULT 'info',"
            "  is_read BOOLEAN NOT NULL DEFAULT FALSE,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_notif_user (user_id),"
            "  INDEX idx_notif_read (user_id, is_read)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
        "audit_logs": (
            "CREATE TABLE IF NOT EXISTS audit_logs ("
            "  id INT AUTO_INCREMENT PRIMARY KEY,"
            "  actor_id INT NOT NULL,"
            "  actor_email VARCHAR(255) NOT NULL,"
            "  action VARCHAR(100) NOT NULL,"
            "  entity_type VARCHAR(100) DEFAULT NULL,"
            "  entity_id INT DEFAULT NULL,"
            "  details TEXT DEFAULT NULL,"
            "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
            "  INDEX idx_audit_actor (actor_id),"
            "  INDEX idx_audit_action (action),"
            "  INDEX idx_audit_created (created_at)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            "  COLLATE=utf8mb4_unicode_ci"
        ),
    }
    for _name, ddl in tables.items():
        try:
            db.execute(ddl)
        except MySQLError:
            pass


# ── singleton ──────────────────────────────────────────

_db_instance: Database | None = None


def get_db() -> Database:
    """Return the shared Database instance (lazy init)."""
    global _db_instance
    if _db_instance is None:
        ensure_database_exists()
        _db_instance = Database()
        run_schema(_db_instance)
        _migrate_day1_corrections(_db_instance)
        _migrate_day3(_db_instance)
        _migrate_day4(_db_instance)
        _migrate_day5(_db_instance)
    return _db_instance
