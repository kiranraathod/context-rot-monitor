
import sqlite3
import datetime
import json
from typing import List, Dict, Any, Optional

class MetricsStore:
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    score REAL,
                    status TEXT,
                    token_count INTEGER,
                    utilization_ratio REAL,
                    relevance_score REAL,
                    redundancy_ratio REAL,
                    step_number INTEGER,
                    model_name TEXT
                )
            """)
            conn.commit()

    def add_record(self, data: Dict[str, Any]):
        """
        Save a health analysis record to the database.
        Expects keys: score, status, metrics(dict), step_number, model
        """
        metrics = data.get("metrics", {})
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO context_health (
                        timestamp, score, status, token_count, utilization_ratio,
                        relevance_score, redundancy_ratio, step_number, model_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.datetime.now().isoformat(),
                    data.get("health_score"),
                    data.get("status"),
                    metrics.get("token_count"),
                    metrics.get("utilization_ratio"),
                    metrics.get("relevance_score", 1.0), # Default to perfect if missing
                    metrics.get("redundancy_ratio", 0.0), # Default to none if missing
                    data.get("step_number"),
                    data.get("model")
                ))
                conn.commit()
        except Exception as e:
            print(f"Error saving metrics: {e}")

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get the most recent health records.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM context_health 
                    ORDER BY id DESC 
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []
