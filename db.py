import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DB_PATH = "research.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    report TEXT NOT NULL,
    sources TEXT NOT NULL,
    duration_seconds REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports (created_at DESC);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    logger.info("Database ready at %s", DB_PATH)


def save_report(question: str, report: str, sources: list, duration_seconds: float = 0) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO reports (question, report, sources, duration_seconds, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                question,
                report,
                json.dumps(sources),
                duration_seconds,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return cur.lastrowid


def list_reports() -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, question, duration_seconds, created_at FROM reports ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_report(report_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["sources"] = json.loads(data["sources"])
        return data


def get_stats() -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, AVG(duration_seconds) AS avg_duration FROM reports"
        ).fetchone()
        return {
            "total_reports": row["total"] or 0,
            "avg_duration_seconds": round(row["avg_duration"], 1) if row["avg_duration"] else 0,
        }
