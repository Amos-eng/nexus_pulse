import asyncio
import psutil
from datetime import datetime
from models import SystemMetric, DatabaseManager


class MetricsCollector:
    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.db = DatabaseManager()

    async def gather_metrics(self) -> SystemMetric:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        status = "HEALTHY"
        if cpu > 85.0 or memory > 90.0:
            status = "CRITICAL"
        elif cpu > 60.0 or memory > 75.0:
            status = "WARNING"

        metric = SystemMetric(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cpu_percent=cpu,
            memory_percent=memory,
            disk_usage=disk,
            status=status,
        )

        self.db.save_metric(metric)
        return metric