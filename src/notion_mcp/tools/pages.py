"""Page tools — wraps PagesMixin methods."""

from __future__ import annotations

import json
from typing import Any

from ..server import mcp, get_client, _parse_json, _error_response


@mcp.tool()
def create_page(
    parent: str,
    properties: str,
    children: str | None = None,
    template: str | None = None,
) -> str:
    """Create a new Notion page.

    Args:
        parent: JSON string for the parent object, e.g. {"type": "page_id", "page_id": "..."}.
        properties: JSON string for the page properties mapping.
        children: Optional JSON string for a list of block children to append.
            Cannot be used together with template.
        template: Optional JSON string for a data-source template, e.g.
            {"type": "none"}, {"type": "default"}, or
            {"type": "template_id", "template_id": "<uuid>"}.
    """
    try:
        result = get_client().create_page(
            parent=_parse_json(parent, "parent"),
            properties=_parse_json(properties, "properties"),
            children=_parse_json(children, "children"),
            template=_parse_json(template, "template"),
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_page(page_id: str) -> str:
    """Retrieve a Notion page by its ID.

    Args:
        page_id: The UUID of the page to retrieve.
    """
    try:
        result = get_client().get_page(page_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_page(
    page_id: str,
    properties: str | None = None,
    erase_content: bool | None = None,
    icon: str | None = None,
    cover: str | None = None,
) -> str:
    """Update a Notion page's properties, icon, or cover.

    Args:
        page_id: The UUID of the page to update.
        properties: Optional JSON string of properties to update.
        erase_content: If true, clears ALL block content from the page.
            WARNING: This is destructive and irreversible.
        icon: Optional JSON string for the page icon.
        cover: Optional JSON string for the page cover.
    """
    try:
        kwargs: dict[str, Any] = {}
        if properties is not None:
            kwargs["properties"] = _parse_json(properties, "properties")
        if icon is not None:
            kwargs["icon"] = _parse_json(icon, "icon")
        if cover is not None:
            kwargs["cover"] = _parse_json(cover, "cover")
        result = get_client().update_page(
            page_id,
            erase_content=erase_content,
            **kwargs,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def archive_page(page_id: str) -> str:
    """Archive (soft-delete) a Notion page.

    Args:
        page_id: The UUID of the page to archive.
    """
    try:
        result = get_client().archive_page(page_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def move_page(page_id: str, parent: str) -> str:
    """Move a Notion page to a new parent.

    Args:
        page_id: The UUID of the page to move.
        parent: JSON string for the new parent object,
            e.g. {"type": "page_id", "page_id": "..."}.
    """
    try:
        result = get_client().move_page(
            page_id,
            parent=_parse_json(parent, "parent"),
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
