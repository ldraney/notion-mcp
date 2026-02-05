"""Comment tools — wraps CommentsMixin methods."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response


@mcp.tool()
def create_comment(
    parent: Annotated[str, Field(description="JSON string for the parent object, e.g. '{\"page_id\": \"...\"}'")],
    rich_text: Annotated[str, Field(description="JSON string for the rich-text content array, e.g. '[{\"type\": \"text\", \"text\": {\"content\": \"Hello!\"}}]'")],
    discussion_id: Annotated[str | None, Field(description="UUID of an existing discussion thread to reply to. Omit to start a new top-level comment.")] = None,
) -> str:
    """Create a comment on a Notion page or block.

    IMPORTANT: parent and rich_text must be passed as JSON-encoded strings, NOT as objects.

    Args:
        parent: JSON string for the parent object,
            e.g. '{"page_id": "..."}'.
        rich_text: JSON string for the rich-text content array,
            e.g. '[{"type": "text", "text": {"content": "Hello!"}}]'.
        discussion_id: Optional UUID of an existing discussion thread
            to reply to. Omit to start a new top-level comment.
    """
    try:
        kwargs: dict[str, object] = {}
        if discussion_id is not None:
            kwargs["discussion_id"] = discussion_id
        result = get_client().create_comment(
            parent=_parse_json(parent, "parent"),
            rich_text=_parse_json(rich_text, "rich_text"),
            **kwargs,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_comments(
    block_id: Annotated[str, Field(description="The UUID of the block or page to list comments for")],
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
) -> str:
    """List comments on a Notion block or page.

    Args:
        block_id: The UUID of the block or page to list comments for.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().get_comments(
            block_id,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
