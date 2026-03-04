"""Time computation engine — pure Python, zero dependencies, <1ms.

Provides current time lookup, timezone difference calculation, time
conversion, business hours overlap, and optional sunrise/sunset via
the ``astral`` library. All functions are stateless and thread-safe.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class CityTimeInfo:
    """Current time information for a timezone."""

    timezone_id: str
    timezone_abbr: str
    utc_offset: str
    utc_offset_hours: float
    current_time: datetime
    is_dst: bool


@dataclass(frozen=True)
class TimeDifferenceInfo:
    """Time difference between two timezones."""

    from_tz: str
    to_tz: str
    difference_hours: float
    difference_str: str
    from_ahead: bool


@dataclass(frozen=True)
class SunInfo:
    """Sunrise and sunset information."""

    sunrise: datetime
    sunset: datetime
    dawn: datetime
    dusk: datetime
    day_length_seconds: int
    is_daytime: bool


# ── Current Time ──────────────────────────────────────────────────


def get_current_time(timezone_id: str) -> CityTimeInfo:
    """Get current time for a timezone.

    Args:
        timezone_id: IANA timezone identifier (e.g., "America/New_York").

    Returns:
        CityTimeInfo with current time, UTC offset, and DST status.
    """
    tz = ZoneInfo(timezone_id)
    now = datetime.now(tz)

    utc_offset = now.utcoffset() or timedelta()
    dst_offset = now.dst() or timedelta()
    is_dst = dst_offset.total_seconds() > 0

    total_seconds = int(utc_offset.total_seconds())
    hours, remainder = divmod(abs(total_seconds), 3600)
    minutes = remainder // 60
    sign = "+" if total_seconds >= 0 else "-"
    offset_str = f"{sign}{hours:02d}:{minutes:02d}"
    offset_hours = total_seconds / 3600

    return CityTimeInfo(
        timezone_id=timezone_id,
        timezone_abbr=now.strftime("%Z"),
        utc_offset=offset_str,
        utc_offset_hours=offset_hours,
        current_time=now,
        is_dst=is_dst,
    )


# ── Time Difference ───────────────────────────────────────────────


def get_time_difference(from_tz: str, to_tz: str) -> TimeDifferenceInfo:
    """Calculate time difference between two timezones.

    Args:
        from_tz: Source IANA timezone (e.g., "America/New_York").
        to_tz: Target IANA timezone (e.g., "Asia/Seoul").

    Returns:
        TimeDifferenceInfo with difference in hours and formatted string.
    """
    now_utc = datetime.now(timezone.utc)
    from_offset = now_utc.astimezone(ZoneInfo(from_tz)).utcoffset() or timedelta()
    to_offset = now_utc.astimezone(ZoneInfo(to_tz)).utcoffset() or timedelta()

    diff_seconds = (to_offset - from_offset).total_seconds()
    diff_hours = diff_seconds / 3600

    diff_str = f"{int(diff_hours):+d}h" if diff_hours == int(diff_hours) else f"{diff_hours:+.1f}h"

    return TimeDifferenceInfo(
        from_tz=from_tz,
        to_tz=to_tz,
        difference_hours=diff_hours,
        difference_str=diff_str,
        from_ahead=diff_hours < 0,
    )


# ── Time Conversion ───────────────────────────────────────────────


def convert_time(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert a datetime from one timezone to another.

    If ``dt`` is naive (no tzinfo), it is assumed to be in ``from_tz``.

    Args:
        dt: Datetime to convert.
        from_tz: Source IANA timezone.
        to_tz: Target IANA timezone.

    Returns:
        Datetime in the target timezone.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(from_tz))
    return dt.astimezone(ZoneInfo(to_tz))


# ── Sunrise / Sunset (optional: astral) ──────────────────────────


def get_sun_info(latitude: float, longitude: float, timezone_id: str) -> SunInfo | None:
    """Calculate sunrise/sunset for given coordinates.

    Requires the ``astral`` library (``pip install timefyi[sun]``).
    Returns ``None`` if astral is not installed or cannot compute
    (e.g., polar regions where the sun doesn't rise/set).

    Args:
        latitude: Latitude in decimal degrees.
        longitude: Longitude in decimal degrees.
        timezone_id: IANA timezone identifier.

    Returns:
        SunInfo with sunrise, sunset, dawn, dusk, day length, and
        daytime flag. None if computation fails.
    """
    try:
        from astral import LocationInfo
        from astral.sun import sun
    except ImportError:
        return None

    tz = ZoneInfo(timezone_id)
    today = datetime.now(tz).date()

    try:
        loc = LocationInfo(
            name="",
            region="",
            timezone=timezone_id,
            latitude=latitude,
            longitude=longitude,
        )
        s = sun(loc.observer, date=today, tzinfo=tz)
    except ValueError:
        # Polar regions where sun doesn't rise/set
        return None

    now = datetime.now(tz)
    sunrise: datetime = s["sunrise"]
    sunset: datetime = s["sunset"]

    return SunInfo(
        sunrise=sunrise,
        sunset=sunset,
        dawn=s["dawn"],
        dusk=s["dusk"],
        day_length_seconds=int((sunset - sunrise).total_seconds()),
        is_daytime=sunrise <= now <= sunset,
    )


# ── Hourly Comparison ─────────────────────────────────────────────


def get_hourly_comparison(from_tz: str, to_tz: str, hours: int = 24) -> list[tuple[int, int]]:
    """Generate hourly time comparison table.

    Args:
        from_tz: Source IANA timezone.
        to_tz: Target IANA timezone.
        hours: Number of hours to compare (default 24).

    Returns:
        List of (from_hour, to_hour) tuples.
    """
    diff = get_time_difference(from_tz, to_tz)
    diff_h = diff.difference_hours
    result: list[tuple[int, int]] = []
    for h in range(hours):
        to_h = (h + diff_h) % 24
        result.append((h, int(to_h)))
    return result


# ── Business Hours Overlap ────────────────────────────────────────


def get_business_hours_overlap(
    timezones: list[str],
    start_hour: int = 9,
    end_hour: int = 18,
) -> list[int]:
    """Find UTC hours where all timezones are within business hours.

    Args:
        timezones: List of IANA timezone identifiers.
        start_hour: Business day start hour (default 9).
        end_hour: Business day end hour (default 18).

    Returns:
        List of UTC hours (0-23) where overlap exists.
    """
    if not timezones:
        return []

    now_utc = datetime.now(timezone.utc)
    offset_hours: list[float] = []
    for tz_id in timezones:
        tz_offset = now_utc.astimezone(ZoneInfo(tz_id)).utcoffset() or timedelta()
        offset_hours.append(tz_offset.total_seconds() / 3600)

    overlap: list[int] = []
    for utc_hour in range(24):
        all_in_business = True
        for oh in offset_hours:
            local_hour = (utc_hour + oh) % 24
            if not (start_hour <= local_hour < end_hour):
                all_in_business = False
                break
        if all_in_business:
            overlap.append(utc_hour)

    return overlap


# ── Formatting Helpers ────────────────────────────────────────────


def format_offset(hours: float) -> str:
    """Format UTC offset as string (e.g., '+09:00', '-05:00', '+05:30').

    Args:
        hours: UTC offset in hours.

    Returns:
        Formatted offset string.
    """
    sign = "+" if hours >= 0 else "-"
    abs_hours = abs(hours)
    h = int(abs_hours)
    m = int((abs_hours - h) * 60)
    return f"{sign}{h:02d}:{m:02d}"


def format_difference(hours: float) -> str:
    """Format time difference as human-readable string.

    Args:
        hours: Time difference in hours.

    Returns:
        Formatted string (e.g., '+9h', '-5h', '+5.5h').
    """
    if hours == int(hours):
        return f"{int(hours):+d}h"
    return f"{hours:+.1f}h"
