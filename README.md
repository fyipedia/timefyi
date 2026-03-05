# timefyi

[![PyPI](https://img.shields.io/pypi/v/timefyi)](https://pypi.org/project/timefyi/)
[![Python](https://img.shields.io/pypi/pyversions/timefyi)](https://pypi.org/project/timefyi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Pure Python timezone engine for developers. Look up current times in any [IANA timezone](https://timefyi.com/worldclock/), compute time differences, find [business hours overlap](https://timefyi.com/) across international teams, convert datetimes, and calculate sunrise/sunset -- all built on stdlib `zoneinfo` with zero core dependencies.

> **Check current times worldwide at [timefyi.com](https://timefyi.com/)** -- [world clock](https://timefyi.com/worldclock/), timezone comparisons, and business hours planning.

<p align="center">
  <img src="demo.gif" alt="timefyi CLI demo" width="800">
</p>

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [Understanding Timezones](#understanding-timezones)
- [Business Hours Across Timezones](#business-hours-across-timezones)
- [Sunrise & Sunset](#sunrise--sunset)
- [Command-Line Interface](#command-line-interface)
- [MCP Server (Claude, Cursor, Windsurf)](#mcp-server-claude-cursor-windsurf)
- [REST API Client](#rest-api-client)
- [API Reference](#api-reference)
  - [Current Time & Conversion](#current-time--conversion)
  - [Business Hours & Comparison](#business-hours--comparison)
  - [Sunrise & Sunset](#sunrise--sunset-1)
  - [Formatting](#formatting)
- [Features](#features)
- [Learn More About Time Zones](#learn-more-about-time-zones)
- [FYIPedia Developer Tools](#fyipedia-developer-tools)
- [License](#license)

## Install

```bash
pip install timefyi              # Core engine (zero deps, uses stdlib zoneinfo)
pip install "timefyi[sun]"       # + Sunrise/sunset (astral)
pip install "timefyi[cli]"       # + Command-line interface
pip install "timefyi[mcp]"       # + MCP server for AI assistants
pip install "timefyi[api]"       # + HTTP client for timefyi.com API
pip install "timefyi[all]"       # Everything
```

## Quick Start

```python
from timefyi import get_current_time, get_time_difference, convert_time

# Current time in Seoul
info = get_current_time("Asia/Seoul")
info.utc_offset           # '+09:00'
info.current_time          # datetime with KST
info.is_dst                # False

# Time difference
diff = get_time_difference("America/New_York", "Asia/Seoul")
diff.difference_hours      # 14.0 (or 13.0 during DST)
diff.difference_str        # '+14h'

# Convert time across timezones
from datetime import datetime
converted = convert_time(datetime(2026, 3, 4, 14, 30), "America/New_York", "Asia/Seoul")
```

## Understanding Timezones

Timezones are governed by the [IANA Time Zone Database](https://www.iana.org/time-zones) (also called `tzdata` or the Olson database), maintained by a volunteer community and released several times per year. Each timezone is identified by a region/city string like `"Asia/Seoul"` or `"America/New_York"` rather than abbreviations like "KST" or "EST" -- because abbreviations are ambiguous ("CST" could mean Central Standard Time, China Standard Time, or Cuba Standard Time).

```python
from timefyi import get_current_time

# Always use IANA identifiers, not abbreviations
seoul = get_current_time("Asia/Seoul")          # UTC+9, no DST
new_york = get_current_time("America/New_York") # UTC-5 (EST) or UTC-4 (EDT)
london = get_current_time("Europe/London")      # UTC+0 (GMT) or UTC+1 (BST)

# DST transitions change the offset
# New York is UTC-5 in winter, UTC-4 in summer
# The "America/New_York" identifier handles this automatically
```

A UTC offset is the number of hours (and sometimes minutes) added to or subtracted from Coordinated Universal Time. Offsets range from UTC-12:00 to UTC+14:00, with several zones at 30- or 45-minute intervals (e.g., India at UTC+5:30, Nepal at UTC+5:45, Chatham Islands at UTC+12:45).

Daylight Saving Time (DST) shifts the local clock forward by one hour during summer months. Not all countries observe DST -- most of Africa, Asia, and South America do not. When DST transitions occur, they happen at different dates in different countries, making timezone arithmetic non-trivial.

## Business Hours Across Timezones

Finding overlapping work hours is one of the most common timezone challenges for distributed teams. A team spanning New York, London, and Seoul has only a narrow window where all three are in standard business hours (9:00-17:00 local).

```python
from timefyi import get_business_hours_overlap, get_hourly_comparison

# Find UTC hours where all timezones are in business hours (9-17 local)
overlap = get_business_hours_overlap(["America/New_York", "Europe/London", "Asia/Seoul"])
# Returns list of overlapping UTC hours

# Side-by-side hour mapping
comparison = get_hourly_comparison("America/New_York", "Asia/Seoul")
# Shows what each hour in New York corresponds to in Seoul
```

## Sunrise & Sunset

```python
# Requires: pip install "timefyi[sun]"
from timefyi import get_sun_info

sun = get_sun_info(37.5665, 126.978, "Asia/Seoul")
sun.sunrise    # datetime — sunrise time
sun.sunset     # datetime — sunset time
```

## Command-Line Interface

```bash
pip install "timefyi[cli]"

timefyi now America/New_York
timefyi diff America/New_York Asia/Seoul
timefyi convert "2026-03-04 14:30" America/New_York Asia/Seoul
timefyi overlap America/New_York Asia/Seoul Europe/London
timefyi sun --lat 37.5665 --lon 126.978 --tz Asia/Seoul
```

## MCP Server (Claude, Cursor, Windsurf)

Add timezone tools to any AI assistant that supports [Model Context Protocol](https://modelcontextprotocol.io/).

```bash
pip install "timefyi[mcp]"
```

Add to your `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "timefyi": {
            "command": "python",
            "args": ["-m", "timefyi.mcp_server"]
        }
    }
}
```

**Available tools**: `current_time`, `time_difference`, `convert_time`, `business_hours_overlap`, `sun_info`

## REST API Client

```python
pip install "timefyi[api]"
```

```python
from timefyi.api import TimeFYI

with TimeFYI() as client:
    result = client.time("seoul")
    diff = client.difference("new-york", "seoul")
```

Full [API documentation](https://timefyi.com/developers/) at timefyi.com.

## API Reference

### Current Time & Conversion

| Function | Description |
|----------|-------------|
| `get_current_time(timezone) -> CityTimeInfo` | Current time with UTC offset, abbreviation, DST status |
| `convert_time(dt, from_tz, to_tz) -> datetime` | Convert datetime between timezones |
| `get_time_difference(tz1, tz2) -> TimeDifferenceInfo` | Hours difference between two timezones |

### Business Hours & Comparison

| Function | Description |
|----------|-------------|
| `get_business_hours_overlap(timezones) -> list` | UTC hours where all timezones are in business hours |
| `get_hourly_comparison(tz1, tz2) -> list` | Side-by-side hour mapping between two timezones |

### Sunrise & Sunset

| Function | Description |
|----------|-------------|
| `get_sun_info(lat, lon, timezone) -> SunInfo` | Dawn, sunrise, sunset, dusk, day length (requires `[sun]`) |

### Formatting

| Function | Description |
|----------|-------------|
| `format_offset(hours) -> str` | Format UTC offset (e.g., "+09:00") |
| `format_difference(hours) -> str` | Format time difference (e.g., "+14h") |

## Features

- **Current time** -- timezone lookup with UTC offset, abbreviation, DST status
- **Time difference** -- hours between any two IANA timezones
- **Time conversion** -- convert datetime across timezones
- **Business hours overlap** -- find UTC hours where multiple timezones overlap
- **Hourly comparison** -- side-by-side hour mapping between timezones
- **Sunrise/sunset** -- dawn, sunrise, sunset, dusk, day length (optional astral)
- **Formatting** -- UTC offset and difference strings
- **CLI** -- Rich terminal output with timezone tables
- **MCP server** -- 5 tools for AI assistants (Claude, Cursor, Windsurf)
- **REST API client** -- httpx-based client for [timefyi.com API](https://timefyi.com/developers/)
- **Zero dependencies** -- core engine uses only stdlib `zoneinfo` and `datetime`
- **Type-safe** -- full type annotations, `py.typed` marker (PEP 561)

## Learn More About Time Zones

- **Tools**: [World Clock](https://timefyi.com/) · [Time Zone Converter](https://timefyi.com/tools/converter/) · [Meeting Planner](https://timefyi.com/tools/meeting/)
- **Browse**: [Time Zones](https://timefyi.com/timezone/) · [Countries](https://timefyi.com/country/)
- **Guides**: [Glossary](https://timefyi.com/glossary/) · [Blog](https://timefyi.com/blog/)
- **API**: [REST API Docs](https://timefyi.com/developers/) · [OpenAPI Spec](https://timefyi.com/api/openapi.json)

## FYIPedia Developer Tools

Part of the [FYIPedia](https://fyipedia.com) open-source developer tools ecosystem.

| Package | PyPI | npm | Description |
|---------|------|-----|-------------|
| colorfyi | [PyPI](https://pypi.org/project/colorfyi/) | [npm](https://www.npmjs.com/package/@fyipedia/colorfyi) | Color conversion, WCAG contrast, harmonies -- [colorfyi.com](https://colorfyi.com/) |
| emojifyi | [PyPI](https://pypi.org/project/emojifyi/) | [npm](https://www.npmjs.com/package/emojifyi) | Emoji encoding & metadata for 3,781 emojis -- [emojifyi.com](https://emojifyi.com/) |
| symbolfyi | [PyPI](https://pypi.org/project/symbolfyi/) | [npm](https://www.npmjs.com/package/symbolfyi) | Symbol encoding in 11 formats -- [symbolfyi.com](https://symbolfyi.com/) |
| unicodefyi | [PyPI](https://pypi.org/project/unicodefyi/) | [npm](https://www.npmjs.com/package/unicodefyi) | Unicode lookup with 17 encodings -- [unicodefyi.com](https://unicodefyi.com/) |
| fontfyi | [PyPI](https://pypi.org/project/fontfyi/) | [npm](https://www.npmjs.com/package/fontfyi) | Google Fonts metadata & CSS -- [fontfyi.com](https://fontfyi.com/) |
| distancefyi | [PyPI](https://pypi.org/project/distancefyi/) | [npm](https://www.npmjs.com/package/distancefyi) | Haversine distance & travel times -- [distancefyi.com](https://distancefyi.com/) |
| **timefyi** | [PyPI](https://pypi.org/project/timefyi/) | [npm](https://www.npmjs.com/package/timefyi) | Timezone ops & business hours -- [timefyi.com](https://timefyi.com/) |
| namefyi | [PyPI](https://pypi.org/project/namefyi/) | [npm](https://www.npmjs.com/package/namefyi) | Korean romanization & Five Elements -- [namefyi.com](https://namefyi.com/) |
| unitfyi | [PyPI](https://pypi.org/project/unitfyi/) | [npm](https://www.npmjs.com/package/unitfyi) | Unit conversion, 220 units -- [unitfyi.com](https://unitfyi.com/) |
| holidayfyi | [PyPI](https://pypi.org/project/holidayfyi/) | [npm](https://www.npmjs.com/package/holidayfyi) | Holiday dates & Easter calculation -- [holidayfyi.com](https://holidayfyi.com/) |
| cocktailfyi | [PyPI](https://pypi.org/project/cocktailfyi/) | -- | Cocktail ABV, calories, flavor -- [cocktailfyi.com](https://cocktailfyi.com/) |
| fyipedia | [PyPI](https://pypi.org/project/fyipedia/) | -- | Unified CLI: `fyi color info FF6B35` -- [fyipedia.com](https://fyipedia.com/) |
| fyipedia-mcp | [PyPI](https://pypi.org/project/fyipedia-mcp/) | -- | Unified MCP hub for AI assistants -- [fyipedia.com](https://fyipedia.com/) |

## License

MIT
