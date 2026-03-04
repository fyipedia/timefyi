"""Command-line interface for timefyi.

Requires: pip install timefyi[cli]

Usage::

    timefyi now America/New_York
    timefyi diff America/New_York Asia/Seoul
    timefyi convert "2026-03-04 14:30" America/New_York Asia/Seoul
    timefyi overlap America/New_York Asia/Seoul Europe/London
    timefyi sun --lat 37.5665 --lon 126.978 --tz Asia/Seoul
"""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="timefyi",
    help="Timezone lookups, time differences, and business hours overlap.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def now(
    timezone_id: str = typer.Argument(help="IANA timezone (e.g., America/New_York)"),
) -> None:
    """Show current time for a timezone."""
    from timefyi import get_current_time

    info = get_current_time(timezone_id)

    table = Table(title=f"Current Time — {timezone_id}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Time", info.current_time.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row("Timezone", f"{info.timezone_abbr} (UTC{info.utc_offset})")
    table.add_row("DST Active", "Yes" if info.is_dst else "No")

    console.print(table)


@app.command()
def diff(
    from_tz: str = typer.Argument(help="Source timezone"),
    to_tz: str = typer.Argument(help="Target timezone"),
) -> None:
    """Show time difference between two timezones."""
    from timefyi import get_current_time, get_time_difference

    result = get_time_difference(from_tz, to_tz)
    from_info = get_current_time(from_tz)
    to_info = get_current_time(to_tz)

    table = Table(title=f"Time Difference — {from_tz} to {to_tz}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Difference", result.difference_str)
    table.add_row(f"{from_tz}", from_info.current_time.strftime("%Y-%m-%d %H:%M:%S"))
    table.add_row(f"{to_tz}", to_info.current_time.strftime("%Y-%m-%d %H:%M:%S"))

    console.print(table)


@app.command("convert")
def convert_cmd(
    time_str: str = typer.Argument(help="Time to convert (e.g., '2026-03-04 14:30')"),
    from_tz: str = typer.Argument(help="Source timezone"),
    to_tz: str = typer.Argument(help="Target timezone"),
) -> None:
    """Convert a time from one timezone to another."""
    from datetime import datetime

    from timefyi import convert_time

    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    converted = convert_time(dt, from_tz, to_tz)

    console.print(f"[cyan]{from_tz}:[/] {time_str}")
    console.print(f"[green]{to_tz}:[/] {converted.strftime('%Y-%m-%d %H:%M:%S %Z')}")


@app.command()
def overlap(
    timezones: list[str] = typer.Argument(help="Two or more IANA timezones"),  # noqa: B008
    start: int = typer.Option(9, help="Business hours start (default 9)"),
    end: int = typer.Option(18, help="Business hours end (default 18)"),
) -> None:
    """Find business hours overlap across timezones."""
    from timefyi import get_business_hours_overlap

    hours = get_business_hours_overlap(timezones, start_hour=start, end_hour=end)

    if not hours:
        console.print("[yellow]No overlapping business hours found.[/]")
        raise typer.Exit(0)

    table = Table(title="Business Hours Overlap (UTC)")
    table.add_column("UTC Hour", style="cyan")
    for tz in timezones:
        table.add_column(tz, style="green")

    from timefyi import get_time_difference

    offsets: list[float] = []
    for tz in timezones:
        diff = get_time_difference("UTC", tz)
        offsets.append(diff.difference_hours)

    for utc_h in hours:
        row = [f"{utc_h:02d}:00"]
        for offset in offsets:
            local_h = int((utc_h + offset) % 24)
            row.append(f"{local_h:02d}:00")
        table.add_row(*row)

    console.print(table)


@app.command("sun")
def sun_cmd(
    lat: float = typer.Option(..., help="Latitude"),
    lon: float = typer.Option(..., help="Longitude"),
    tz: str = typer.Option(..., help="IANA timezone"),
) -> None:
    """Show sunrise/sunset for a location (requires timefyi[sun])."""
    from timefyi import get_sun_info

    info = get_sun_info(lat, lon, tz)
    if info is None:
        console.print("[red]Cannot compute sun times (astral not installed or polar region).[/]")
        raise typer.Exit(1)

    table = Table(title=f"Sun Info — {tz}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Dawn", info.dawn.strftime("%H:%M:%S"))
    table.add_row("Sunrise", info.sunrise.strftime("%H:%M:%S"))
    table.add_row("Sunset", info.sunset.strftime("%H:%M:%S"))
    table.add_row("Dusk", info.dusk.strftime("%H:%M:%S"))
    hours = info.day_length_seconds // 3600
    minutes = (info.day_length_seconds % 3600) // 60
    table.add_row("Day Length", f"{hours}h {minutes:02d}m")
    table.add_row("Daytime", "Yes" if info.is_daytime else "No")

    console.print(table)
