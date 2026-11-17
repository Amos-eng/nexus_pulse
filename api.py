import sqlite3
from fastapi import FastAPI, HTTPException
import psutil

app = FastAPI(
    title="NexusPulse Telemetry API",
    description="Pro-tier system telemetry and historical analytics microservice.",
    version="1.0.0"
)

DB_FILE = "nexus_metrics.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "NexusPulse Telemetry API",
        "endpoints": ["/metrics/live", "/metrics/history"]
    }

@app.get("/metrics/live")
def get_live_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            "status": "success",
            "cpu_percent": cpu_usage,
            "memory": {
                "total_mb": round(memory.total / (1024 * 1024), 2),
                "used_mb": round(memory.used / (1024 * 1024), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "percent": disk.percent
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/history")
def get_historical_metrics(limit: int = 20):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM metrics ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {
            "status": "success",
            "count": len(rows),
            "data": rows
        }
    except Exception as e:
        return {
            "status": "warning",
            "message": "Metrics table not found or empty. Run monitor.py to populate historical data.",
            "error": str(e)
        }
