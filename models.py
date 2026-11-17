import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DB_PATH = Path("nexus_metrics.db")

@dataclass
class SystemMetric:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    status: str

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    disk_usage REAL NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_metric(self, metric: SystemMetric):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO metrics (timestamp, cpu_percent, memory_percent, disk_usage, status)
                VALUES (?, ?, ?, ?, ?)
            """, (metric.timestamp, metric.cpu_percent, metric.memory_percent, metric.disk_usage, metric.status))
            conn.commit()

    def get_historical_stats(self):
        """Calculates aggregate averages and peaks across all recorded metrics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*), 
                    AVG(cpu_percent), MAX(cpu_percent), 
                    AVG(memory_percent), MAX(memory_percent),
                    AVG(disk_usage), MAX(disk_usage)
                FROM metrics
            """)
            return cursor.fetchone()

    def get_all_metrics(self):
        """Fetches every logged telemetry record for export."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, cpu_percent, memory_percent, disk_usage, status 
                FROM metrics ORDER BY id ASC
            """)
            return cursor.fetchall()