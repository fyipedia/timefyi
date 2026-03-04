"""MCP server for timefyi — timezone tools for AI assistants.

Requires: pip install timefyi[mcp]

Configure in claude_desktop_config.json::

    {
        "mcpServers": {
            "timefyi": {
                "command": "python",
                "args": ["-m", "timefyi.mcp_server"]
            }
        }
    }
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("timefyi")


@mcp.tool()
def current_time(timezone_id: str) -> str:
    """Get current time for a timezone.

    Args:
        timezone_id: IANA timezone identifier (e.g., "America/New_York", "Asia/Seoul").
    """
    from timefyi import get_current_time

    info = get_current_time(timezone_id)

    lines = [
        f"## Current Time — {timezone_id}",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| Time | {info.current_time.strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| Timezone | {info.timezone_abbr} (UTC{info.utc_offset}) |",
        f"| DST Active | {'Yes' if info.is_dst else 'No'} |",
    ]

    return "\n".join(lines)


@mcp.tool()
def time_difference(from_tz: str, to_tz: str) -> str:
    """Calculate time difference between two timezones.

    Args:
        from_tz: Source IANA timezone (e.g., "America/New_York").
        to_tz: Target IANA timezone (e.g., "Asia/Seoul").
    """
    from timefyi import get_current_time, get_time_difference

    diff = get_time_difference(from_tz, to_tz)
    from_info = get_current_time(from_tz)
    to_info = get_current_time(to_tz)

    lines = [
        f"## Time Difference: {diff.difference_str}",
        "",
        "| Timezone | Current Time |",
        "|----------|-------------|",
        f"| {from_tz} | {from_info.current_time.strftime('%Y-%m-%d %H:%M:%S')} |",
        f"| {to_tz} | {to_info.current_time.strftime('%Y-%m-%d %H:%M:%S')} |",
    ]

    return "\n".join(lines)


@mcp.tool()
def convert_time(time_str: str, from_tz: str, to_tz: str) -> str:
    """Convert a time from one timezone to another.

    Args:
        time_str: Time string in 'YYYY-MM-DD HH:MM' format.
        from_tz: Source IANA timezone.
        to_tz: Target IANA timezone.
    """
    from datetime import datetime

    from timefyi import convert_time as _convert_time

    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    converted = _convert_time(dt, from_tz, to_tz)

    return f"{from_tz}: {time_str}\n{to_tz}: {converted.strftime('%Y-%m-%d %H:%M:%S %Z')}"


@mcp.tool()
def business_hours_overlap(timezones: list[str], start_hour: int = 9, end_hour: int = 18) -> str:
    """Find UTC hours where all timezones have overlapping business hours.

    Args:
        timezones: List of IANA timezone identifiers.
        start_hour: Business day start hour (default 9).
        end_hour: Business day end hour (default 18).
    """
    from timefyi import get_business_hours_overlap

    hours = get_business_hours_overlap(timezones, start_hour=start_hour, end_hour=end_hour)

    if not hours:
        return "No overlapping business hours found."

    lines = [
        "## Business Hours Overlap",
        "",
        f"**{len(hours)} overlapping hours (UTC):** {', '.join(f'{h:02d}:00' for h in hours)}",
    ]

    return "\n".join(lines)


@mcp.tool()
def sun_info(latitude: float, longitude: float, timezone_id: str) -> str:
    """Get sunrise/sunset times for a location (requires astral library).

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        timezone_id: IANA timezone identifier.
    """
    from timefyi import get_sun_info

    info = get_sun_info(latitude, longitude, timezone_id)
    if info is None:
        return "Cannot compute sun times (astral not installed or polar region)."

    hours = info.day_length_seconds // 3600
    minutes = (info.day_length_seconds % 3600) // 60

    lines = [
        f"## Sun Info — {timezone_id}",
        "",
        "| Property | Value |",
        "|----------|-------|",
        f"| Dawn | {info.dawn.strftime('%H:%M:%S')} |",
        f"| Sunrise | {info.sunrise.strftime('%H:%M:%S')} |",
        f"| Sunset | {info.sunset.strftime('%H:%M:%S')} |",
        f"| Dusk | {info.dusk.strftime('%H:%M:%S')} |",
        f"| Day Length | {hours}h {minutes:02d}m |",
        f"| Daytime | {'Yes' if info.is_daytime else 'No'} |",
    ]

    return "\n".join(lines)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
