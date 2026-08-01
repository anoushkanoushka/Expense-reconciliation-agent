import sqlite3

DB_PATH = "recon.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT,
            transaction_desc TEXT,
            transaction_amount REAL,
            decision TEXT,
            receipt_id TEXT,
            confidence TEXT,
            clarifying_question TEXT,
            reasoning TEXT,
            resolved INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def save_match(result: dict) -> None:
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO matches
        (transaction_date, transaction_desc, transaction_amount, decision, receipt_id, confidence, clarifying_question, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            result.get("transaction_date"),
            result.get("transaction_desc"),
            result.get("transaction_amount"),
            result.get("decision"),
            result.get("receipt_id"),
            result.get("confidence"),
            result.get("clarifying_question"),
            result.get("reasoning"),
        ),
    )
    conn.commit()
    conn.close()


def get_all_matches() -> list:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM matches ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_needs_clarification() -> list:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM matches WHERE decision = 'needs_clarification' AND resolved = 0"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def resolve_match(match_id: int, receipt_id: str) -> None:
    conn = get_connection()
    conn.execute(
        """
        UPDATE matches
        SET decision = 'matched', receipt_id = ?, resolved = 1
        WHERE id = ?
    """,
        (receipt_id, match_id),
    )
    conn.commit()
    conn.close()
