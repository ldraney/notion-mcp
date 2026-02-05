"""MCP server entry point — FastMCP app and NotionClient lifecycle."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from notion_sdk import NotionClient

mcp = FastMCP("notion")

# ---------------------------------------------------------------------------
# Shared client instance
# ---------------------------------------------------------------------------

_client: NotionClient | None = None


def get_client() -> NotionClient:
    """Return the shared NotionClient, creating it on first call.

    The client reads NOTION_API_KEY from the environment (via the SDK).
    """
    global _client
    if _client is None:
        _client = NotionClient()
    return _client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json(value: str | dict | list | None, name: str) -> Any:
    """Parse a JSON string into a Python object, or pass through if already parsed."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for parameter '{name}': {exc}") from exc


def _error_response(exc: Exception) -> str:
    """Format an exception into a user-friendly error string."""
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            body = exc.response.json()
        except Exception:
            body = exc.response.text
        return json.dumps(
            {
                "error": True,
                "status_code": exc.response.status_code,
                "message": str(exc),
                "details": body,
            },
            indent=2,
        )
    return json.dumps({"error": True, "message": str(exc)}, indent=2)


# ---------------------------------------------------------------------------
# Register tool modules — each module calls @mcp.tool() at import time
# ---------------------------------------------------------------------------

from .tools import register_all_tools  # noqa: E402

register_all_tools()
