"""Application configuration — loads and validates environment variables."""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    """Return env var value or exit with a clear message."""
    value = os.getenv(key)
    if not value:
        print(f"[FATAL] Missing required environment variable: {key}")
        print("Copy .env.example to .env and fill in the values.")
        sys.exit(1)
    return value


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# ── MySQL ──────────────────────────────────────────────
MYSQL_HOST: str = _optional("MYSQL_HOST", "localhost")
MYSQL_PORT: int = int(_optional("MYSQL_PORT", "3306"))
MYSQL_DATABASE: str = _require("MYSQL_DATABASE")
MYSQL_USER: str = _require("MYSQL_USER")
MYSQL_PASSWORD: str = _require("MYSQL_PASSWORD")

# ── Application ────────────────────────────────────────
SECRET_KEY: str = _require("SECRET_KEY")
ENVIRONMENT: str = _optional("ENVIRONMENT", "development")

# ── Admin bootstrap ────────────────────────────────────
ADMIN_EMAIL: str = _require("ADMIN_EMAIL")
ADMIN_PASSWORD: str = _require("ADMIN_PASSWORD")

# ── AI providers ───────────────────────────────────────
# Gemini/OpenAI remain available for the existing AI features.
GEMINI_API_KEY: str = _optional("GEMINI_API_KEY")
OPENAI_API_KEY: str = _optional("OPENAI_API_KEY")

# Groq is used by the live opportunity discovery module only.
GROQ_API_KEY: str = _optional("GROQ_API_KEY")

# ── Paths ──────────────────────────────────────────────
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
SCHEMA_PATH: str = os.path.join(BASE_DIR, "database", "schema.sql")
