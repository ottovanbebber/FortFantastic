"""
Fort Fantastic - Database Setup
================================
Creates the SQLite reference database from schema.sql.

Usage:
    python db/setup_database.py

Run this ONCE before seeding. Safe to re-run — drops and recreates all tables.
The database file is created at: db/fort_fantastic.db
"""

import sqlite3
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
DB_PATH     = os.path.join(BASE_DIR, "fort_fantastic.db")


def create_database() -> sqlite3.Connection:
    """
    Create (or recreate) the Fort Fantastic reference database.

    Reads schema.sql and executes all CREATE TABLE statements.
    Returns an open connection to the database.
    """
    print(f"[setup] Database path : {DB_PATH}")
    print(f"[setup] Schema path   : {SCHEMA_PATH}")

    # Load schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Connect (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")  # better concurrent read performance

    # Apply schema
    conn.executescript(schema_sql)
    conn.commit()

    print("[setup] Schema applied successfully.")
    return conn


def verify_tables(conn: sqlite3.Connection) -> None:
    """Print all created tables to confirm setup."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    print(f"[setup] Tables created ({len(tables)}): {', '.join(tables)}")


if __name__ == "__main__":
    conn = create_database()
    verify_tables(conn)
    conn.close()
    print("[setup] Done. Run seed_data.py to populate the database.")
