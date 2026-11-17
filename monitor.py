import asyncio
from dataclasses import dataclass
from datetime import datetime

import psutil


@dataclass
class Metric:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    status: str


class MetricsCollector:
    """Collects system metrics asynchronously.

    The blocking psutil calls are off-loaded to a worker thread via
    asyncio.to_thread so the Rich Live display stays responsive.
    """

    def __init__(self, interval: float = 1.5, db=None):
        self.interval = interval
        self.db = db  # optional DatabaseManager for persistence
        # Prime CPU measurement (first call returns 0.0)
        psutil.cpu_percent(interval=None)

    def _read_metrics(self) -> Metric:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if cpu >= 85 or memory >= 85 or disk >= 90:
            status = "CRITICAL"
        elif cpu >= 70 or memory >= 70 or disk >= 80:
            status = "WARNING"
        else:
            status = "HEALTHY"

        return Metric(
            timestamp=ts,
            cpu_percent=round(cpu, 1),
            memory_percent=round(memory, 1),
            disk_usage=round(disk, 1),
            status=status,
        )

    async def gather_metrics(self) -> Metric:
        # Non-blocking: run the synchronous psutil snapshot in a thread
        metric = await asyncio.to_thread(self._read_metrics)

        if self.db is not None:
            await asyncio.to_thread(
                self.db.insert_metric,
                metric.timestamp,
                metric.cpu_percent,
                metric.memory_percent,
                metric.disk_usage,
                metric.status,
            )
        return metric