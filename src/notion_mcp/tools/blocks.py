"""Block tools — wraps BlocksMixin methods."""

from __future__ import annotations

import json
from typing import Annotated, Any

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response


@mcp.tool()
def get_block(
    block_id: Annotated[str, Field(description="The UUID of the block to retrieve")],
) -> str:
    """Retrieve a Notion block by its ID.

    Args:
        block_id: The UUID of the block to retrieve.
    """
    try:
        result = get_client().get_block(block_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_block_children(
    block_id: Annotated[str, Field(description="The UUID of the parent block")],
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
) -> str:
    """List child blocks of a Notion block.

    Args:
        block_id: The UUID of the parent block.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().get_block_children(
            block_id,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def append_block_children(
    block_id: Annotated[str, Field(description="The UUID of the parent block to append children to")],
    children: Annotated[str | list, Field(description="JSON string or array for a list of block objects to append")],
) -> str:
    """Append child blocks to a Notion block.

    Args:
        block_id: The UUID of the parent block to append children to.
        children: JSON string or array for a list of block objects to append.
    """
    try:
        result = get_client().append_block_children(
            block_id,
            children=_parse_json(children, "children"),
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_block(
    block_id: Annotated[str, Field(description="The UUID of the block to update")],
    content: Annotated[str | dict | None, Field(description="JSON string or object of block properties to update. The keys depend on the block type, e.g. {\"paragraph\": {\"rich_text\": [...]}}")] = None,
) -> str:
    """Update a Notion block.

    Args:
        block_id: The UUID of the block to update.
        content: JSON string or object of block properties to update. The keys depend
            on the block type (e.g. {"paragraph": {"rich_text": [...]}}).
    """
    try:
        kwargs: dict[str, Any] = {}
        if content is not None:
            kwargs = _parse_json(content, "content")
        result = get_client().update_block(block_id, **kwargs)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def delete_block(
    block_id: Annotated[str, Field(description="The UUID of the block to delete")],
) -> str:
    """Delete (archive) a Notion block.

    Args:
        block_id: The UUID of the block to delete.
    """
    try:
        result = get_client().delete_block(block_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
