import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional

DB_PATH = Path(__file__).parent / "nexus_pulse.db"


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path: Path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu REAL NOT NULL,
                    memory REAL NOT NULL,
                    disk REAL NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def insert_metric(self, timestamp: str, cpu: float, memory: float,
                      disk: float, status: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO metrics (timestamp, cpu, memory, disk, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (timestamp, cpu, memory, disk, status),
            )
            conn.commit()

    def get_historical_stats(self) -> Optional[Tuple[int, float, float, float,
                                                      float, float, float]]:
        """Return flat tuple: (count, avg_cpu, max_cpu, avg_mem, max_mem,
        avg_disk, max_disk). Returns (0, 0, 0, 0, 0, 0, 0) if empty."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT COUNT(*),
                       COALESCE(AVG(cpu), 0),    COALESCE(MAX(cpu), 0),
                       COALESCE(AVG(memory), 0), COALESCE(MAX(memory), 0),
                       COALESCE(AVG(disk), 0),   COALESCE(MAX(disk), 0)
                FROM metrics
                """
            ).fetchone()

        # sqlite returns a single row; make sure it's a flat 7-tuple
        if not row:
            return (0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return tuple(row)  # type: ignore[return-value]

    def get_all_metrics(self) -> List[Tuple[str, float, float, float, str]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT timestamp, cpu, memory, disk, status "
                "FROM metrics ORDER BY id ASC"
            ).fetchall()
        return rows