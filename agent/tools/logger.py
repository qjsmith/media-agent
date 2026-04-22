import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_DIR = Path(__file__).parent.parent.parent / "db"


def get_db_path() -> Path:
    """Return the path to today's database file."""
    today = datetime.now().strftime("%Y-%m-%d")
    return DB_DIR / f"media_agent_{today}.db"


def init_db():
    """Create the database and tables if they don't exist."""
    db_path = get_db_path()
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
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
    """Log an agent decision to today's database."""
    init_db()
    conn = sqlite3.connect(get_db_path())
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
    """Retrieve recent decisions from today's database."""
    init_db()
    conn = sqlite3.connect(get_db_path())
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


def get_summary() -> dict:
    """Return a count of each action type from today's database."""
    init_db()
    conn = sqlite3.connect(get_db_path())
    rows = conn.execute("""
        SELECT action, COUNT(*) as count
        FROM decisions
        GROUP BY action
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


if __name__ == "__main__":
    print(f"DB: {get_db_path()}")
    print("\nSummary:")
    summary = get_summary()
    if not summary:
        print("  No decisions logged yet.")
    for action, count in summary.items():
        print(f"  {action}: {count}")

    print("\nRecent decisions:")
    decisions = get_recent_decisions()
    if not decisions:
        print("  No decisions logged yet.")
    for d in decisions:
        print(d)