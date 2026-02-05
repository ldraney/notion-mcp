"""User tools — wraps UsersMixin methods."""

from __future__ import annotations

import json

from ..server import mcp, get_client, _error_response


@mcp.tool()
def get_users(
    start_cursor: str | None = None,
    page_size: int | None = None,
) -> str:
    """List all users in the Notion workspace.

    Args:
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().get_users(
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_self() -> str:
    """Retrieve the bot user associated with the current API token."""
    try:
        result = get_client().get_self()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
