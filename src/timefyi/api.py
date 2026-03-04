"""HTTP API client for timefyi.com REST endpoints.

Requires: pip install timefyi[api]

Usage::

    from timefyi.api import TimeFYI

    with TimeFYI() as client:
        result = client.time("seoul")
        print(result["timezone_id"])
"""

from __future__ import annotations

from typing import Any

import httpx


class TimeFYI:
    """API client for the timefyi.com REST API."""

    def __init__(
        self,
        base_url: str = "https://timefyi.com/api",
        timeout: float = 10.0,
    ) -> None:
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        resp = self._client.get(path, params={k: v for k, v in params.items() if v is not None})
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result

    def time(self, city_slug: str) -> dict[str, Any]:
        """Get current time for a city by slug.

        Args:
            city_slug: City slug (e.g., "seoul", "new-york").

        Returns:
            Dict with timezone_id, current_time, utc_offset, etc.
        """
        return self._get(f"/time/{city_slug}/")

    def difference(self, from_slug: str, to_slug: str) -> dict[str, Any]:
        """Get time difference between two cities.

        Args:
            from_slug: Source city slug (e.g., "new-york").
            to_slug: Target city slug (e.g., "seoul").

        Returns:
            Dict with difference_hours, difference_str, etc.
        """
        return self._get(f"/difference/{from_slug}-to-{to_slug}/")

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for cities by name.

        Args:
            query: Search query string.
            limit: Maximum results to return.

        Returns:
            List of matching city dicts.
        """
        result = self._get("/search/", q=query, limit=limit)
        if isinstance(result, list):
            return list(result)
        results: list[dict[str, Any]] = result.get("results", [])
        return results

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> TimeFYI:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
