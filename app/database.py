import os

import libsql_experimental as libsql
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


def get_db_connection():
    """Get a Turso/libSQL connection."""
    if not TURSO_DATABASE_URL or not TURSO_AUTH_TOKEN:
        raise ValueError(
            "TURSO_DATABASE_URL and TURSO_AUTH_TOKEN must be set. "
            "Copy .env.example to .env and add your Turso credentials."
        )
    return libsql.connect(database=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)


def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    # Create recipes table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
