"""Page tools — wraps PagesMixin methods."""

from __future__ import annotations

import json
from typing import Annotated, Any

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response, _slim_response


@mcp.tool()
def create_page(
    parent: Annotated[str | dict, Field(description="JSON string or object for the parent, e.g. {\"type\": \"page_id\", \"page_id\": \"...\"}")],
    properties: Annotated[str | dict, Field(description="JSON string or object for the page properties mapping")],
    children: Annotated[str | list | None, Field(description="JSON string or array for a list of block children to append. Cannot be used together with template.")] = None,
    template: Annotated[str | dict | None, Field(description="JSON string or object for a data-source template, e.g. {\"type\": \"none\"}, {\"type\": \"default\"}, or {\"type\": \"template_id\", \"template_id\": \"<uuid>\"}")] = None,
    position: Annotated[str | dict | None, Field(description='Optional position object to control where content is inserted. Valid types: {"type": "page_start"}, {"type": "page_end"}, {"type": "after_block", "after_block": {"id": "<block_id>"}}')] = None,
    icon: Annotated[str | dict | None, Field(description="JSON string or object for the page icon, e.g. {\"type\": \"emoji\", \"emoji\": \"...\"}")] = None,
    cover: Annotated[str | dict | None, Field(description="JSON string or object for the page cover, e.g. {\"type\": \"external\", \"external\": {\"url\": \"https://...\"}}")] = None,
) -> str:
    """Create a new Notion page.

    Args:
        parent: JSON string or object for the parent object, e.g. {"type": "page_id", "page_id": "..."}.
        properties: JSON string or object for the page properties mapping.
        children: Optional JSON string or array for a list of block children to append.
            Cannot be used together with template.
        template: Optional JSON string or object for a data-source template, e.g.
            {"type": "none"}, {"type": "default"}, or
            {"type": "template_id", "template_id": "<uuid>"}.
        position: Optional position object to control where content is inserted.
        icon: Optional JSON string or object for the page icon.
        cover: Optional JSON string or object for the page cover.
    """
    try:
        kwargs: dict[str, Any] = dict(
            parent=_parse_json(parent, "parent"),
            properties=_parse_json(properties, "properties"),
            children=_parse_json(children, "children"),
            template=_parse_json(template, "template"),
        )
        if position is not None:
            kwargs["position"] = _parse_json(position, "position")
        if icon is not None:
            kwargs["icon"] = _parse_json(icon, "icon")
        if cover is not None:
            kwargs["cover"] = _parse_json(cover, "cover")
        result = get_client().create_page(**kwargs)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_page(
    page_id: Annotated[str, Field(description="The UUID of the page to retrieve")],
    filter_properties: Annotated[str | list | None, Field(description="Optional list of property IDs to include in the response. Pass as a JSON array of strings or a list.")] = None,
) -> str:
    """Retrieve a Notion page by its ID.

    Args:
        page_id: The UUID of the page to retrieve.
        filter_properties: Optional list of property IDs to include in the response.
    """
    try:
        kwargs: dict[str, Any] = {}
        if filter_properties is not None:
            kwargs["filter_properties"] = _parse_json(filter_properties, "filter_properties")
        result = get_client().get_page(page_id, **kwargs)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_page_property_item(
    page_id: Annotated[str, Field(description="The UUID of the page")],
    property_id: Annotated[str, Field(description="The ID of the property to retrieve")],
    start_cursor: Annotated[str | None, Field(description="Cursor for paginated property values (e.g. rollups)")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page for paginated properties")] = None,
) -> str:
    """Retrieve a page property item. Essential for relations, rollups, and long rich_text.

    Args:
        page_id: The UUID of the page.
        property_id: The ID of the property to retrieve.
        start_cursor: Cursor for paginated property values (e.g. rollups).
        page_size: Number of results per page for paginated properties.
    """
    try:
        result = get_client().get_page_property_item(
            page_id,
            property_id,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_page(
    page_id: Annotated[str, Field(description="The UUID of the page to update")],
    properties: Annotated[str | dict | None, Field(description="JSON string or object of properties to update")] = None,
    erase_content: Annotated[bool | None, Field(description="If true, clears ALL block content from the page. WARNING: This is destructive and irreversible.")] = None,
    icon: Annotated[str | dict | None, Field(description="JSON string or object for the page icon, e.g. {\"type\": \"emoji\", \"emoji\": \"...\"}")] = None,
    cover: Annotated[str | dict | None, Field(description="JSON string or object for the page cover, e.g. {\"type\": \"external\", \"external\": {\"url\": \"https://...\"}}")] = None,
) -> str:
    """Update a Notion page's properties, icon, or cover.

    Args:
        page_id: The UUID of the page to update.
        properties: Optional JSON string or object of properties to update.
        erase_content: If true, clears ALL block content from the page.
            WARNING: This is destructive and irreversible.
        icon: Optional JSON string or object for the page icon.
        cover: Optional JSON string or object for the page cover.
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
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def archive_page(
    page_id: Annotated[str, Field(description="The UUID of the page to archive")],
) -> str:
    """Archive (soft-delete) a Notion page.

    Args:
        page_id: The UUID of the page to archive.
    """
    try:
        result = get_client().archive_page(page_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def move_page(
    page_id: Annotated[str, Field(description="The UUID of the page to move")],
    parent: Annotated[str | dict, Field(description="JSON string or object for the new parent, e.g. {\"type\": \"page_id\", \"page_id\": \"...\"}")],
) -> str:
    """Move a Notion page to a new parent.

    Args:
        page_id: The UUID of the page to move.
        parent: JSON string or object for the new parent object,
            e.g. {"type": "page_id", "page_id": "..."}.
    """
    try:
        result = get_client().move_page(
            page_id,
            parent=_parse_json(parent, "parent"),
        )
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
