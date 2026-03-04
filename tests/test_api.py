"""Tests for the timefyi API client."""

from timefyi.api import TimeFYI


def test_client_init() -> None:
    """Client initializes with default URL."""
    client = TimeFYI()
    assert str(client._client.base_url).rstrip("/") == "https://timefyi.com/api"
    client.close()


def test_client_custom_url() -> None:
    """Client accepts custom base URL."""
    client = TimeFYI(base_url="https://custom.example.com/api")
    assert str(client._client.base_url).rstrip("/") == "https://custom.example.com/api"
    client.close()


def test_client_context_manager() -> None:
    """Client works as context manager."""
    with TimeFYI() as client:
        assert client._client is not None
