"""User tools — wraps UsersMixin methods."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


@mcp.tool()
def get_users(
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
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
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_user(
    user_id: Annotated[str, Field(description="The UUID of the user to retrieve")],
) -> str:
    """Retrieve a Notion user by their ID.

    Args:
        user_id: The UUID of the user to retrieve.
    """
    try:
        result = get_client().get_user(user_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_self() -> str:
    """Retrieve the bot user associated with the current API token."""
    try:
        result = get_client().get_self()
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
