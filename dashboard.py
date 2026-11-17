import asyncio
import argparse
import csv
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from models import DatabaseManager
from monitor import MetricsCollector

console = Console()


def show_history() -> None:
    """Query SQLite and print historical statistics using a Rich table."""
    db = DatabaseManager()
    stats = db.get_historical_stats()

    if not stats or stats[0] == 0:
        console.print(
            "[yellow]No historical metrics found in database yet. "
            "Run the live dashboard first![/yellow]"
        )
        return

    count, avg_cpu, max_cpu, avg_mem, max_mem, avg_disk, max_disk = stats

    table = Table(
        title="NexusPulse Historical Analytics",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("System Metric", style="cyan")
    table.add_column("Average Usage", justify="right", style="green")
    table.add_column("Peak / Maximum", justify="right", style="red")

    table.add_row("CPU Utilization", f"{avg_cpu:.1f}%", f"{max_cpu:.1f}%")
    table.add_row("Memory Utilization", f"{avg_mem:.1f}%", f"{max_mem:.1f}%")
    table.add_row("Disk Utilization", f"{avg_disk:.1f}%", f"{max_disk:.1f}%")

    console.print(
        f"\n[bold green]✓ Total Telemetry Records Analyzed:[/bold green] {count}\n"
    )
    console.print(table)


def export_to_csv(filename: str) -> None:
    """Export all SQLite telemetry records to a CSV file."""
    db = DatabaseManager()
    rows = db.get_all_metrics()

    if not rows:
        console.print("[yellow]No metrics available in database to export.[/yellow]")
        return

    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "CPU (%)", "Memory (%)", "Disk (%)", "Status"])
            writer.writerows(rows)
        console.print(
            f"[bold green]Successfully exported {len(rows)} records to "
            f"'{filename}'![/bold green]"
        )
    except Exception as e:
        console.print(f"[bold red]Failed to export file: {e}[/bold red]")


def generate_dashboard(metric) -> Layout:
    layout = Layout()

    header = Panel(
        "[bold cyan]NEXUS-PULSE V1.0[/bold cyan] | "
        "Enterprise Telemetry & Health Engine",
        style="white on blue",
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Timestamp", style="dim")
    table.add_column("CPU Usage", justify="right")
    table.add_column("Memory Usage", justify="right")
    table.add_column("Disk Usage", justify="right")
    table.add_column("System Status", justify="center")

    status_color = {
        "HEALTHY": "green",
        "WARNING": "yellow",
        "CRITICAL": "red",
    }.get(metric.status, "white")

    table.add_row(
        metric.timestamp,
        f"{metric.cpu_percent}%",
        f"{metric.memory_percent}%",
        f"{metric.disk_usage}%",
        f"[{status_color}]{metric.status}[/{status_color}]",
    )

    layout.split(
        Layout(header, size=3),
        Layout(Panel(table, title="Live Telemetry Stream")),
    )
    return layout


async def main() -> None:
    db = DatabaseManager()
    collector = MetricsCollector(interval=1.5, db=db)

    console.print("[green]Initializing NexusPulse Diagnostic Core...[/green]")
    await asyncio.sleep(1)

    try:
        with Live(console=console, refresh_per_second=4) as live:
            while True:
                metric = await collector.gather_metrics()
                live.update(generate_dashboard(metric))
                await asyncio.sleep(collector.interval)
    except KeyboardInterrupt:
        console.print("[bold red]Telemetry stream terminated safely.[/bold red]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="NexusPulse: Advanced Asynchronous System Telemetry & Analytics"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Display aggregated historical analytics from SQLite",
    )
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILENAME",
        help="Export all recorded telemetry logs to a CSV file",
    )

    args = parser.parse_args()

    if args.history:
        show_history()
    elif args.export:
        export_to_csv(args.export)
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            pass  # already reported inside main()