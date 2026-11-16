import sqlite3
from unittest.mock import patch
import pytest
from models import DatabaseManager, SystemMetric
from monitor import MetricsCollector


@pytest.fixture
def temp_db(tmp_path):
    """Provides a clean, isolated SQLite database for each test."""
    db_file = tmp_path / "test_nexus.db"
    return DatabaseManager(db_path=db_file)


def test_database_initialization(temp_db):
    """Verify the metrics table is created on startup."""
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='metrics';"
        )
        assert cursor.fetchone() is not None


def test_save_metric_persists_data(temp_db):
    """Verify a SystemMetric dataclass writes accurately to SQLite."""
    sample = SystemMetric(
        timestamp="2026-11-17 01:30:00",
        cpu_percent=42.5,
        memory_percent=61.0,
        disk_usage=55.2,
        status="HEALTHY",
    )
    temp_db.save_metric(sample)

    with sqlite3.connect(temp_db.db_path) as conn:
        row = conn.execute(
            "SELECT cpu_percent, memory_percent, status FROM metrics"
        ).fetchone()

    assert row == (42.5, 61.0, "HEALTHY")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cpu, mem, expected_status",
    [
        (25.0, 40.0, "HEALTHY"),
        (65.0, 50.0, "WARNING"),
        (30.0, 80.0, "WARNING"),
        (90.0, 50.0, "CRITICAL"),
        (40.0, 95.0, "CRITICAL"),
    ],
)
async def test_collector_status_thresholds(
    tmp_path, cpu, mem, expected_status
):
    """Verify HEALTHY, WARNING, and CRITICAL threshold boundaries."""
    collector = MetricsCollector(interval=0.1)
    collector.db = DatabaseManager(db_path=tmp_path / "threshold_test.db")

    with (
        patch("monitor.psutil.cpu_percent", return_value=cpu),
        patch("monitor.psutil.virtual_memory") as mock_mem,
        patch("monitor.psutil.disk_usage") as mock_disk,
    ):
        mock_mem.return_value.percent = mem
        mock_disk.return_value.percent = 50.0

        metric = await collector.gather_metrics()
        assert metric.status == expected_status