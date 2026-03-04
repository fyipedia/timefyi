"""Tests for the timefyi engine."""

from datetime import datetime
from zoneinfo import ZoneInfo

from timefyi import (
    CityTimeInfo,
    SunInfo,
    TimeDifferenceInfo,
    convert_time,
    format_difference,
    format_offset,
    get_business_hours_overlap,
    get_current_time,
    get_hourly_comparison,
    get_sun_info,
    get_time_difference,
)

# ── get_current_time ──


def test_current_time_seoul() -> None:
    """Seoul should be UTC+9 (or +9 with no DST)."""
    info = get_current_time("Asia/Seoul")
    assert isinstance(info, CityTimeInfo)
    assert info.timezone_id == "Asia/Seoul"
    assert info.utc_offset == "+09:00"
    assert info.utc_offset_hours == 9.0
    assert info.is_dst is False


def test_current_time_new_york() -> None:
    """New York should return a valid CityTimeInfo."""
    info = get_current_time("America/New_York")
    assert isinstance(info, CityTimeInfo)
    assert info.timezone_id == "America/New_York"
    # UTC offset is either -5 or -4 depending on DST
    assert info.utc_offset_hours in (-5.0, -4.0)


def test_current_time_utc() -> None:
    """UTC offset should be +00:00."""
    info = get_current_time("UTC")
    assert info.utc_offset == "+00:00"
    assert info.utc_offset_hours == 0.0
    assert info.is_dst is False


def test_current_time_half_offset() -> None:
    """India has a +5:30 offset."""
    info = get_current_time("Asia/Kolkata")
    assert info.utc_offset == "+05:30"
    assert info.utc_offset_hours == 5.5


# ── get_time_difference ──


def test_time_difference_seoul_utc() -> None:
    """Seoul is +9h from UTC."""
    diff = get_time_difference("UTC", "Asia/Seoul")
    assert isinstance(diff, TimeDifferenceInfo)
    assert diff.difference_hours == 9.0
    assert diff.difference_str == "+9h"
    assert diff.from_ahead is False


def test_time_difference_same_timezone() -> None:
    """Same timezone should have 0 difference."""
    diff = get_time_difference("Asia/Seoul", "Asia/Seoul")
    assert diff.difference_hours == 0.0
    assert diff.difference_str == "+0h"


def test_time_difference_negative() -> None:
    """Seoul to New York should be negative (NY is behind)."""
    diff = get_time_difference("Asia/Seoul", "America/New_York")
    # Depending on DST: -14h or -13h
    assert diff.difference_hours in (-14.0, -13.0)
    assert diff.from_ahead is True


def test_time_difference_half_hour() -> None:
    """India offset includes half-hour."""
    diff = get_time_difference("UTC", "Asia/Kolkata")
    assert diff.difference_hours == 5.5
    assert diff.difference_str == "+5.5h"


# ── convert_time ──


def test_convert_time_naive() -> None:
    """Naive datetime should be treated as from_tz."""
    dt = datetime(2026, 3, 4, 14, 30)
    result = convert_time(dt, "America/New_York", "Asia/Seoul")
    assert result.tzinfo is not None
    # 14:30 EST → next day 04:30 KST (during EST, +14h)
    # 14:30 EDT → next day 03:30 KST (during EDT, +13h)
    assert result.hour in (3, 4)


def test_convert_time_aware() -> None:
    """Aware datetime should ignore from_tz and use existing tzinfo."""
    dt = datetime(2026, 1, 15, 12, 0, tzinfo=ZoneInfo("UTC"))
    result = convert_time(dt, "America/New_York", "Asia/Seoul")
    # UTC 12:00 → KST 21:00
    assert result.hour == 21


def test_convert_time_same_tz() -> None:
    """Converting to same timezone should keep the same time."""
    dt = datetime(2026, 6, 15, 10, 0)
    result = convert_time(dt, "Asia/Seoul", "Asia/Seoul")
    assert result.hour == 10


# ── get_sun_info ──


def test_sun_info_seoul() -> None:
    """Seoul should have valid sunrise/sunset."""
    info = get_sun_info(37.5665, 126.978, "Asia/Seoul")
    assert info is not None
    assert isinstance(info, SunInfo)
    assert info.sunrise < info.sunset
    assert info.dawn < info.sunrise
    assert info.sunset < info.dusk
    assert info.day_length_seconds > 0


def test_sun_info_day_length() -> None:
    """Day length should be between 0 and 86400 seconds (24h)."""
    info = get_sun_info(51.5074, -0.1278, "Europe/London")
    assert info is not None
    assert 0 < info.day_length_seconds < 86400


# ── get_hourly_comparison ──


def test_hourly_comparison_length() -> None:
    """Should return 24 tuples by default."""
    result = get_hourly_comparison("UTC", "Asia/Seoul")
    assert len(result) == 24


def test_hourly_comparison_custom_hours() -> None:
    """Custom hours parameter."""
    result = get_hourly_comparison("UTC", "Asia/Seoul", hours=12)
    assert len(result) == 12


def test_hourly_comparison_values() -> None:
    """Seoul is +9 from UTC, so UTC 0:00 → KST 9:00."""
    result = get_hourly_comparison("UTC", "Asia/Seoul")
    # First entry: (0, 9) — UTC midnight → KST 9am
    assert result[0] == (0, 9)


# ── get_business_hours_overlap ──


def test_business_hours_overlap_empty() -> None:
    """Empty timezone list should return empty."""
    assert get_business_hours_overlap([]) == []


def test_business_hours_overlap_single() -> None:
    """Single timezone should return 9 hours (9-18)."""
    result = get_business_hours_overlap(["UTC"])
    assert len(result) == 9


def test_business_hours_overlap_two_close() -> None:
    """Two close timezones should have significant overlap."""
    result = get_business_hours_overlap(["Europe/London", "Europe/Paris"])
    # London and Paris are 0-1h apart, should have 8-9 hours overlap
    assert len(result) >= 8


def test_business_hours_overlap_far_apart() -> None:
    """Distant timezones may have limited or no overlap."""
    result = get_business_hours_overlap(["America/New_York", "Asia/Seoul"])
    # NY and Seoul are 13-14h apart, very limited overlap
    assert len(result) <= 4


def test_business_hours_overlap_custom_hours() -> None:
    """Custom start/end hours."""
    result = get_business_hours_overlap(["UTC"], start_hour=8, end_hour=20)
    assert len(result) == 12


# ── format_offset ──


def test_format_offset_positive() -> None:
    assert format_offset(9.0) == "+09:00"


def test_format_offset_negative() -> None:
    assert format_offset(-5.0) == "-05:00"


def test_format_offset_zero() -> None:
    assert format_offset(0.0) == "+00:00"


def test_format_offset_half() -> None:
    assert format_offset(5.5) == "+05:30"


def test_format_offset_quarter() -> None:
    assert format_offset(5.75) == "+05:45"


# ── format_difference ──


def test_format_difference_positive() -> None:
    assert format_difference(9.0) == "+9h"


def test_format_difference_negative() -> None:
    assert format_difference(-5.0) == "-5h"


def test_format_difference_zero() -> None:
    assert format_difference(0.0) == "+0h"


def test_format_difference_half() -> None:
    assert format_difference(5.5) == "+5.5h"
