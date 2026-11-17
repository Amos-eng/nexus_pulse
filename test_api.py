from fastapi.testclient import TestClient
from api import app

# Initialize the test client using FastAPI's built-in TestClient
client = TestClient(app)

def test_read_root():
    """Test the root health-check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "NexusPulse Telemetry API"
    assert "/metrics/live" in data["endpoints"]

def test_get_live_metrics():
    """Test the real-time system metrics endpoint."""
    response = client.get("/metrics/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "cpu_percent" in data
    assert "memory" in data
    assert "disk" in data
    # Verify values are populated correctly
    assert isinstance(data["cpu_percent"], (int, float))
    assert data["memory"]["percent"] >= 0

def test_get_historical_metrics():
    """Test the historical metrics endpoint query parameters and structure."""
    response = client.get("/metrics/history?limit=5")
    assert response.status_code == 200
    data = response.json()
    # It will return success or a warning if the database/table isn't seeded yet
    assert "status" in data
    if data["status"] == "success":
        assert isinstance(data["data"], list)
        assert data["count"] <= 5