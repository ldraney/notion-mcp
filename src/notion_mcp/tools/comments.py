"""Comment tools — wraps CommentsMixin methods."""

from __future__ import annotations

import json

from ..server import mcp, get_client, _parse_json, _error_response


@mcp.tool()
def create_comment(
    parent: str,
    rich_text: str,
    discussion_id: str | None = None,
) -> str:
    """Create a comment on a Notion page or block.

    Args:
        parent: JSON string for the parent object,
            e.g. {"page_id": "..."}.
        rich_text: JSON string for the rich-text content array,
            e.g. [{"type": "text", "text": {"content": "Hello!"}}].
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
    block_id: str,
    start_cursor: str | None = None,
    page_size: int | None = None,
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
