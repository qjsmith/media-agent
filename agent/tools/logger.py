import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "db" / "media_agent.db"

def init_db():
    """Create the database and tables if they don't exist."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            filename TEXT NOT NULL,
            action TEXT NOT NULL,
            reasoning TEXT,
            success INTEGER NOT NULL,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_decision(filename: str, action: str, reasoning: str, success: bool, details: dict = None):
    """Log an agent decision to the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO decisions (timestamp, filename, action, reasoning, success, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        filename,
        action,
        reasoning,
        int(success),
        json.dumps(details or {})
    ))
    conn.commit()
    conn.close()


def get_recent_decisions(limit: int = 20) -> list[dict]:
    """Retrieve recent decisions from the database."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT timestamp, filename, action, reasoning, success, details
        FROM decisions
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "timestamp": r[0],
            "filename": r[1],
            "action": r[2],
            "reasoning": r[3],
            "success": bool(r[4]),
            "details": json.loads(r[5])
        }
        for r in rows
    ]


if __name__ == "__main__":
    print("Recent decisions:")
    decisions = get_recent_decisions()
    if not decisions:
        print("  No decisions logged yet.")
    for d in decisions:
        print(d)