import asyncio
import json
from pathlib import Path
import psutil
from datetime import datetime
from models import SystemMetric, DatabaseManager

CONFIG_PATH = Path("config.json")
ALERT_LOG_PATH = Path("nexus_alerts.log")

class MetricsCollector:
    def __init__(self, interval: float = None, db = None, **kwargs):
        self.config = self._load_config()
        self.interval = interval if interval is not None else self.config.get("interval", 1.5)
        self.db = db if db is not None else DatabaseManager()

    def _load_config(self) -> dict:
        """Loads configuration from config.json or falls back to safe defaults."""
        default_config = {
            "interval": 1.5,
            "cpu_warning": 60.0,
            "cpu_critical": 85.0,
            "memory_warning": 75.0,
            "memory_critical": 90.0,
            "disk_critical": 90.0
        }
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    return {**default_config, **json.load(f)}
            except Exception:
                return default_config
        return default_config

    def _log_alert(self, message: str):
        """Appends system warnings and critical alerts to a local log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ALERT_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")

    async def gather_metrics(self) -> SystemMetric:
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        status = "HEALTHY"
        if cpu >= self.config["cpu_critical"] or memory >= self.config["memory_critical"] or disk >= self.config["disk_critical"]:
            status = "CRITICAL"
            self._log_alert(f"CRITICAL SPIKE DETECTED -> CPU: {cpu}%, MEM: {memory}%, DISK: {disk}%")
        elif cpu >= self.config["cpu_warning"] or memory >= self.config["memory_warning"]:
            status = "WARNING"
            self._log_alert(f"WARNING THRESHOLD REACHED -> CPU: {cpu}%, MEM: {memory}%")

        metric = SystemMetric(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            cpu_percent=cpu,
            memory_percent=memory,
            disk_usage=disk,
            status=status
        )
        
        self.db.save_metric(metric)
        return metric