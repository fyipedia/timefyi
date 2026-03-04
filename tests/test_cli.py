"""Tests for the timefyi CLI."""

from typer.testing import CliRunner

from timefyi.cli import app

runner = CliRunner()


def test_now_command() -> None:
    result = runner.invoke(app, ["now", "Asia/Seoul"])
    assert result.exit_code == 0
    assert "Current Time" in result.output


def test_now_utc() -> None:
    result = runner.invoke(app, ["now", "UTC"])
    assert result.exit_code == 0
    assert "UTC" in result.output


def test_diff_command() -> None:
    result = runner.invoke(app, ["diff", "America/New_York", "Asia/Seoul"])
    assert result.exit_code == 0
    assert "Time Difference" in result.output


def test_convert_command() -> None:
    result = runner.invoke(app, ["convert", "2026-03-04 14:30", "America/New_York", "Asia/Seoul"])
    assert result.exit_code == 0
    assert "America/New_York" in result.output
    assert "Asia/Seoul" in result.output


def test_overlap_command() -> None:
    result = runner.invoke(app, ["overlap", "Europe/London", "Europe/Paris"])
    assert result.exit_code == 0
    assert "Business Hours" in result.output


def test_sun_command() -> None:
    result = runner.invoke(
        app,
        ["sun", "--lat", "37.5665", "--lon", "126.978", "--tz", "Asia/Seoul"],
    )
    assert result.exit_code == 0
    assert "Sun Info" in result.output
