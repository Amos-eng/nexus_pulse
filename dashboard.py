import asyncio
from monitor import MetricsCollector


async def main():
    collector = MetricsCollector(interval=2.0)
    print("Nexus Pulse running. Press Ctrl+C to stop.\n")
    while True:
        m = await collector.gather_metrics()
        print(
            f"{m.timestamp} | CPU {m.cpu_percent:5.1f}% | "
            f"MEM {m.memory_percent:5.1f}% | DISK {m.disk_usage:5.1f}% | {m.status}"
        )
        await asyncio.sleep(collector.interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
