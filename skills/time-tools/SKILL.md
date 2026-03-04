---
name: time-tools
description: Get current time, compare timezones, convert time, find business hours overlap, sunrise/sunset.
---

# Time Tools

Timezone operations and time calculations powered by [timefyi](https://timefyi.com/) -- a pure Python timezone engine with zero dependencies.

## Setup

Install the MCP server:

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

## Available Tools

| Tool | Description |
|------|-------------|
| `current_time` | Get the current time in any timezone |
| `time_difference` | Calculate the time difference between two timezones |
| `convert_time` | Convert a specific time from one timezone to another |
| `business_hours_overlap` | Find overlapping business hours between two timezones |
| `sun_info` | Get sunrise and sunset times for a location |

## When to Use

- Checking the current time in a different city or timezone
- Scheduling meetings across multiple timezones
- Finding overlapping work hours for distributed teams
- Converting specific times between timezones
- Looking up sunrise and sunset times

## Links

- [World Clock](https://timefyi.com/) -- Current time in every timezone
- [API Documentation](https://timefyi.com/developers/) -- Free REST API
- [PyPI Package](https://pypi.org/project/timefyi/)
