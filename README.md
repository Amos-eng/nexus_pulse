# NexusPulse ⚡

[![NexusPulse CI](https://github.com/Amos-eng/nexus_pulse/actions/workflows/test.yml/badge.svg)](https://github.com/Amos-eng/nexus_pulse/actions/workflows/test.yml)

Asynchronous system telemetry engine, CLI analytics tool, and automated threshold alerting monitor built with Python.

## Features
- **Real-Time Dashboard:** Live-updating terminal UI powered by `rich` and `psutil`.
- **SQLite Persistence:** Historical metric logging (`nexus_metrics.db`) with CLI query and CSV export support.
- **Externalized Configuration:** Dynamic threshold management via `config.json`.
- **Automated Alerting:** Logs warning and critical resource spikes to `nexus_alerts.log`.
- **CI/CD Verified:** Automated `pytest` and `pytest-asyncio` validation via GitHub Actions.

## Quickstart

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the live telemetry dashboard
python dashboard.py
