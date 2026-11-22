import sqlite3
from pathlib import Path
from database.schema import SCHEMA

DB_PATH = Path(__file__).resolve().parent.parent / "career_tracker.db"


def get_connection():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con


def initialize_database():
    with get_connection() as con:
        con.executescript(SCHEMA)

        columns = {
            row["name"]
            for row in con.execute(
                "PRAGMA table_info(applications)"
            ).fetchall()
        }

        additions = {
            "company": "TEXT DEFAULT ''",
            "role": "TEXT DEFAULT ''",
            "location": "TEXT DEFAULT ''",
            "applied_date": "TEXT DEFAULT ''",
            "status": "TEXT DEFAULT 'Applied'",
            "notes": "TEXT DEFAULT ''",
            "created_at": "TEXT DEFAULT ''",
            "company_id": "INTEGER",
        }

        for name, definition in additions.items():
            if name not in columns:
                con.execute(
                    f"ALTER TABLE applications ADD COLUMN {name} {definition}"
                )

        con.execute("""
            UPDATE applications
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL OR created_at = ''
        """)

        rows = con.execute("""
            SELECT id, company
            FROM applications
            WHERE company_id IS NULL
        """).fetchall()

        for row in rows:
            company_name = (row["company"] or "").strip()

            if company_name:
                con.execute(
                    "INSERT OR IGNORE INTO companies(name) VALUES (?)",
                    (company_name,)
                )

                company = con.execute(
                    "SELECT id FROM companies WHERE name = ? COLLATE NOCASE",
                    (company_name,)
                ).fetchone()

                if company:
                    con.execute(
                        "UPDATE applications SET company_id = ? WHERE id = ?",
                        (company["id"], row["id"])
                    )

        con.commit()


def query(sql, params=()):
    with get_connection() as con:
        return con.execute(sql, params).fetchall()


def execute(sql, params=()):
    with get_connection() as con:
        cursor = con.execute(sql, params)
        con.commit()
        return cursor.lastrowid