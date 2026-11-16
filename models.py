import sqlite3
from dataclasses import dataclass


@dataclass
class SystemMetric:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    status: str


class DatabaseManager:
    def __init__(self, db_path: str = "nexus_pulse.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    disk_usage REAL NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )

    def save_metric(self, metric: SystemMetric) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_usage, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    metric.timestamp,
                    metric.cpu_percent,
                    metric.memory_percent,
                    metric.disk_usage,
                    metric.status,
                ),
            )

    def get_recent(self, limit: int = 20) -> list[SystemMetric]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT timestamp, cpu_percent, memory_percent, disk_usage, status "
                "FROM metrics ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [SystemMetric(*row) for row in rows]
