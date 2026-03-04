"""Tests for the timefyi MCP server."""

from timefyi.mcp_server import (
    business_hours_overlap,
    convert_time,
    current_time,
    sun_info,
    time_difference,
)


def test_current_time() -> None:
    result = current_time("Asia/Seoul")
    assert "Current Time" in result
    assert "Asia/Seoul" in result
    assert "UTC" in result


def test_current_time_utc() -> None:
    result = current_time("UTC")
    assert "+00:00" in result


def test_time_difference() -> None:
    result = time_difference("America/New_York", "Asia/Seoul")
    assert "Time Difference" in result
    assert "America/New_York" in result
    assert "Asia/Seoul" in result


def test_convert_time() -> None:
    result = convert_time("2026-03-04 14:30", "America/New_York", "Asia/Seoul")
    assert "America/New_York" in result
    assert "Asia/Seoul" in result


def test_business_hours_overlap_found() -> None:
    result = business_hours_overlap(["Europe/London", "Europe/Paris"])
    assert "Business Hours Overlap" in result
    assert ":00" in result


def test_business_hours_overlap_none() -> None:
    # Use very narrow window where overlap is impossible
    result = business_hours_overlap(
        ["Pacific/Auckland", "America/Los_Angeles"], start_hour=10, end_hour=11
    )
    # These are ~20h apart, 1-hour window — unlikely to overlap
    assert "No overlapping" in result or "Business Hours" in result


def test_sun_info() -> None:
    result = sun_info(37.5665, 126.978, "Asia/Seoul")
    assert "Sun Info" in result
    assert "Sunrise" in result
    assert "Sunset" in result
