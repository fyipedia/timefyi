# timefyi

Pure Python timezone engine — current time, time differences, business hours overlap, sunrise/sunset. Zero dependencies core.

## Install

```bash
pip install timefyi              # Core (zero deps, uses stdlib zoneinfo)
pip install "timefyi[sun]"       # + sunrise/sunset (astral)
pip install "timefyi[cli]"       # + CLI (typer, rich)
pip install "timefyi[mcp]"       # + MCP server
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

# Convert time
from datetime import datetime
converted = convert_time(datetime(2026, 3, 4, 14, 30), "America/New_York", "Asia/Seoul")

# Business hours overlap
from timefyi import get_business_hours_overlap
hours = get_business_hours_overlap(["America/New_York", "Asia/Seoul", "Europe/London"])
# Returns list of UTC hours where all are in business hours

# Sunrise/sunset (requires timefyi[sun])
from timefyi import get_sun_info
sun = get_sun_info(37.5665, 126.978, "Asia/Seoul")
sun.sunrise    # datetime
sun.sunset     # datetime
```

## Features

- **Current time** — timezone lookup with UTC offset, abbreviation, DST status
- **Time difference** — hours between any two IANA timezones
- **Time conversion** — convert datetime across timezones
- **Business hours overlap** — find UTC hours where multiple timezones overlap
- **Hourly comparison** — side-by-side hour mapping between timezones
- **Sunrise/sunset** — dawn, sunrise, sunset, dusk, day length (optional astral)
- **Formatting** — UTC offset and difference strings

## CLI

```bash
timefyi now America/New_York
timefyi diff America/New_York Asia/Seoul
timefyi convert "2026-03-04 14:30" America/New_York Asia/Seoul
timefyi overlap America/New_York Asia/Seoul Europe/London
timefyi sun --lat 37.5665 --lon 126.978 --tz Asia/Seoul
```

## MCP Server

Add to your Claude Desktop config:

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

Tools: `current_time`, `time_difference`, `convert_time`, `business_hours_overlap`, `sun_info`

## API Client

```python
from timefyi.api import TimeFYI

with TimeFYI() as client:
    result = client.time("seoul")
    diff = client.difference("new-york", "seoul")
```

## License

MIT
