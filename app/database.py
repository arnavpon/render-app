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

    # Create cuisines table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cuisines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Create tags table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Create recipes table (without URL - URLs are in separate table)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine_id INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cuisine_id) REFERENCES cuisines(id)
        )
    """)

    # Create recipe_urls table for multiple URLs per recipe
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recipe_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        )
    """)

    # Create recipe_tags junction table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recipe_tags (
            recipe_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (recipe_id, tag_id),
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
