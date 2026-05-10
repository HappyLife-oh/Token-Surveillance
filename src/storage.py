import sqlite3
import os
from .models import UsageLog, DailySummary


class Storage:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model_name TEXT NOT NULL,
                token_count INTEGER NOT NULL,
                balance_after REAL
            );
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT NOT NULL,
                total_tokens INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                model_name TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (date, model_name)
            );
        """)
        self.conn.commit()

    def insert_usage(self, model_name: str, token_count: int, balance_after: float):
        self.conn.execute(
            "INSERT INTO usage_log (model_name, token_count, balance_after) VALUES (?, ?, ?)",
            (model_name, token_count, balance_after),
        )
        self.conn.commit()

    def get_recent_calls(self, limit: int = 3) -> list[UsageLog]:
        rows = self.conn.execute(
            "SELECT id, timestamp, model_name, token_count, balance_after "
            "FROM usage_log ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [UsageLog(
            id=r["id"], timestamp=r["timestamp"], model_name=r["model_name"],
            token_count=r["token_count"], balance_after=r["balance_after"],
        ) for r in rows]

    def upsert_daily_summary(self, date: str, tokens: int, sessions: int, model_name: str = ""):
        self.conn.execute("""
            INSERT INTO daily_summary (date, total_tokens, total_sessions, model_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date, model_name) DO UPDATE SET
                total_tokens = excluded.total_tokens,
                total_sessions = excluded.total_sessions
        """, (date, tokens, sessions, model_name))
        self.conn.commit()

    def get_weekly_summary(self, days: int = 7) -> list[DailySummary]:
        rows = self.conn.execute("""
            SELECT date, SUM(total_tokens) as total_tokens, SUM(total_sessions) as total_sessions
            FROM daily_summary
            WHERE date >= date('now', ? || ' days')
            GROUP BY date ORDER BY date ASC
        """, (f"-{days}",)).fetchall()
        return [DailySummary(
            date=r["date"], total_tokens=r["total_tokens"],
            total_sessions=r["total_sessions"],
        ) for r in rows]

    def close(self):
        self.conn.close()
