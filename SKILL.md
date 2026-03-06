---
name: time-tools
description: Look up current time in any IANA timezone, compute time differences, find business hours overlap across teams, and calculate sunrise/sunset. Use when working with timezones, scheduling meetings, or converting times.
license: MIT
metadata:
  author: fyipedia
  version: "0.1.1"
  homepage: "https://timefyi.com/"
---

# TimeFYI -- Timezone Tools for AI Agents

Pure Python timezone engine. Look up current times, compute timezone differences, find business hours overlap, convert datetimes, and calculate sunrise/sunset -- built on stdlib `zoneinfo` with zero core dependencies.

**Install**: `pip install timefyi` -- **Web**: [timefyi.com](https://timefyi.com/) -- **API**: [REST API](https://timefyi.com/developers/) -- **npm**: `npm install timefyi`

## When to Use

- User asks what time it is in a specific city or timezone
- User needs the time difference between two timezones
- User wants to find overlapping business hours across multiple timezones
- User asks to convert a datetime from one timezone to another
- User needs sunrise/sunset times for a location

## Tools

### `get_current_time(timezone_id) -> CityTimeInfo`

Get current time for any IANA timezone.

```python
from timefyi import get_current_time

info = get_current_time("Asia/Seoul")
info.timezone_id      # 'Asia/Seoul'
info.timezone_abbr    # 'KST'
info.utc_offset       # '+09:00'
info.utc_offset_hours # 9.0
info.current_time     # datetime with KST tzinfo
info.is_dst           # False
```

### `get_time_difference(from_tz, to_tz) -> TimeDifferenceInfo`

Calculate hours difference between two timezones.

```python
from timefyi import get_time_difference

diff = get_time_difference("America/New_York", "Asia/Seoul")
diff.difference_hours  # 14.0 (or 13.0 during DST)
diff.difference_str    # '+14h'
diff.from_ahead        # False (Seoul is ahead)
```

### `convert_time(dt, from_tz, to_tz) -> datetime`

Convert a datetime from one timezone to another.

```python
from datetime import datetime
from timefyi import convert_time

converted = convert_time(datetime(2026, 3, 4, 14, 30), "America/New_York", "Asia/Seoul")
# datetime with Asia/Seoul tzinfo
```

### `get_business_hours_overlap(timezones, start_hour, end_hour) -> list[int]`

Find UTC hours where all timezones are within business hours.

```python
from timefyi import get_business_hours_overlap

overlap = get_business_hours_overlap(
    ["America/New_York", "Europe/London", "Asia/Seoul"],
    start_hour=9,
    end_hour=18,
)
# List of UTC hours (0-23) where overlap exists
```

### `get_hourly_comparison(from_tz, to_tz, hours) -> list[tuple[int, int]]`

Generate side-by-side hourly time comparison table.

```python
from timefyi import get_hourly_comparison

comparison = get_hourly_comparison("America/New_York", "Asia/Seoul")
# [(0, 14), (1, 15), (2, 16), ...] — 24 hour pairs
```

### `get_sun_info(latitude, longitude, timezone_id) -> SunInfo | None`

Calculate sunrise/sunset for given coordinates. Requires `pip install "timefyi[sun]"`.

```python
from timefyi import get_sun_info

sun = get_sun_info(37.5665, 126.978, "Asia/Seoul")
sun.sunrise             # datetime
sun.sunset              # datetime
sun.dawn                # datetime (civil twilight)
sun.dusk                # datetime
sun.day_length_seconds  # int
sun.is_daytime          # bool
```

### `format_offset(hours) -> str`

Format UTC offset as string.

```python
from timefyi import format_offset

format_offset(9.0)    # '+09:00'
format_offset(-5.5)   # '-05:30'
```

### `format_difference(hours) -> str`

Format time difference as human-readable string.

```python
from timefyi import format_difference

format_difference(14.0)   # '+14h'
format_difference(-5.5)   # '-5.5h'
```

## REST API (No Auth Required)

```bash
curl https://timefyi.com/api/time/seoul/
curl https://timefyi.com/api/difference/new-york/seoul/
curl https://timefyi.com/api/convert/new-york/seoul/?time=14:30
curl https://timefyi.com/api/overlap/new-york/london/seoul/
```

Full spec: [OpenAPI 3.1.0](https://timefyi.com/api/openapi.json)

## Common Timezone Reference

| City | IANA Timezone | UTC Offset |
|------|--------------|------------|
| New York | America/New_York | -05:00 / -04:00 (DST) |
| Los Angeles | America/Los_Angeles | -08:00 / -07:00 (DST) |
| London | Europe/London | +00:00 / +01:00 (DST) |
| Paris | Europe/Paris | +01:00 / +02:00 (DST) |
| Mumbai | Asia/Kolkata | +05:30 |
| Seoul | Asia/Seoul | +09:00 |
| Tokyo | Asia/Tokyo | +09:00 |
| Sydney | Australia/Sydney | +10:00 / +11:00 (DST) |

## Demo

![TimeFYI demo](https://raw.githubusercontent.com/fyipedia/timefyi/main/demo.gif)

## Utility FYI Family

Part of the [FYIPedia](https://fyipedia.com) ecosystem: [UnitFYI](https://unitfyi.com), [TimeFYI](https://timefyi.com), [HolidayFYI](https://holidayfyi.com), [NameFYI](https://namefyi.com), [DistanceFYI](https://distancefyi.com).
