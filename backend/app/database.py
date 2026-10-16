import sqlite3
from pathlib import Path

DB_PATH = Path("data/helpdesk.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def connect():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def initialise():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL
            )
        """)
