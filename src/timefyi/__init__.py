"""timefyi — Pure Python timezone engine for developers.

Look up current time, compute time differences, find business hours
overlap, and get sunrise/sunset info. Zero dependencies core (zoneinfo
is stdlib).

Basic usage::

    >>> from timefyi import get_current_time, get_time_difference
    >>> info = get_current_time("Asia/Seoul")
    >>> info.utc_offset
    '+09:00'
    >>> diff = get_time_difference("America/New_York", "Asia/Seoul")
    >>> diff.difference_hours
    14.0
"""

from timefyi.engine import (
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

__version__ = "0.1.0"

__all__ = [
    # Data types
    "CityTimeInfo",
    "TimeDifferenceInfo",
    "SunInfo",
    # Current time
    "get_current_time",
    # Time difference
    "get_time_difference",
    # Time conversion
    "convert_time",
    # Sunrise / sunset
    "get_sun_info",
    # Hourly comparison
    "get_hourly_comparison",
    # Business hours
    "get_business_hours_overlap",
    # Formatting
    "format_offset",
    "format_difference",
]
