"""Database and data source tools — wraps DatabasesMixin methods."""

from __future__ import annotations

import json
from typing import Any

from ..server import mcp, get_client, _parse_json, _error_response


# ---------------------------------------------------------------------------
# Database tools
# ---------------------------------------------------------------------------


@mcp.tool()
def create_database(
    parent: str,
    title: str,
    initial_data_source: str | None = None,
) -> str:
    """Create a new Notion database.

    In Notion API v2025-09-03, database properties live on data sources.
    Pass properties inside initial_data_source.properties.

    IMPORTANT: All structured parameters must be passed as JSON-encoded strings, NOT as objects.

    Args:
        parent: JSON string for the parent object, e.g. '{"type": "page_id", "page_id": "..."}'.
        title: JSON string for the title rich-text array,
            e.g. '[{"type": "text", "text": {"content": "My DB"}}]'.
        initial_data_source: Optional JSON string for the initial data source
            configuration including properties.
    """
    try:
        result = get_client().create_database(
            parent=_parse_json(parent, "parent"),
            title=_parse_json(title, "title"),
            initial_data_source=_parse_json(initial_data_source, "initial_data_source"),
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_database(database_id: str) -> str:
    """Retrieve a Notion database by its ID.

    Note: In v2025-09-03 the response contains data_sources but NOT
    properties. Use get_data_source to inspect properties.

    Args:
        database_id: The UUID of the database to retrieve.
    """
    try:
        result = get_client().get_database(database_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_database(
    database_id: str,
    title: str | None = None,
    description: str | None = None,
    icon: str | None = None,
    cover: str | None = None,
) -> str:
    """Update a Notion database.

    IMPORTANT: All structured parameters must be passed as JSON-encoded strings, NOT as objects.

    Args:
        database_id: The UUID of the database to update.
        title: Optional JSON string for the new title rich-text array.
        description: Optional JSON string for the description rich-text array.
        icon: Optional JSON string for the database icon.
        cover: Optional JSON string for the database cover.
    """
    try:
        kwargs: dict[str, Any] = {}
        if title is not None:
            kwargs["title"] = _parse_json(title, "title")
        if description is not None:
            kwargs["description"] = _parse_json(description, "description")
        if icon is not None:
            kwargs["icon"] = _parse_json(icon, "icon")
        if cover is not None:
            kwargs["cover"] = _parse_json(cover, "cover")
        result = get_client().update_database(database_id, **kwargs)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def archive_database(database_id: str) -> str:
    """Archive a Notion database.

    Args:
        database_id: The UUID of the database to archive.
    """
    try:
        result = get_client().archive_database(database_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def query_database(
    database_id: str,
    filter: str | None = None,
    sorts: str | None = None,
    start_cursor: str | None = None,
    page_size: int | None = None,
) -> str:
    """Query a Notion database for pages/rows.

    Automatically resolves the first data source and queries it.
    If you already know the data source ID, use query_data_source instead.

    IMPORTANT: filter and sorts must be passed as JSON-encoded strings, NOT as objects.

    Args:
        database_id: The UUID of the database to query.
        filter: Optional JSON string for a filter object.
        sorts: Optional JSON string for a list of sort objects.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().query_database(
            database_id,
            filter=_parse_json(filter, "filter"),
            sorts=_parse_json(sorts, "sorts"),
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


# ---------------------------------------------------------------------------
# Data source tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_data_source(data_source_id: str) -> str:
    """Retrieve a Notion data source (includes properties).

    Args:
        data_source_id: The UUID of the data source to retrieve.
    """
    try:
        result = get_client().get_data_source(data_source_id)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def update_data_source(
    data_source_id: str,
    properties: str | None = None,
) -> str:
    """Update a Notion data source.

    IMPORTANT: The properties parameter must be passed as a JSON-encoded string, NOT as an object.

    Args:
        data_source_id: The UUID of the data source to update.
        properties: Optional JSON string for properties to update.
    """
    try:
        kwargs: dict[str, Any] = {}
        if properties is not None:
            kwargs["properties"] = _parse_json(properties, "properties")
        result = get_client().update_data_source(data_source_id, **kwargs)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def query_data_source(
    data_source_id: str,
    filter: str | None = None,
    sorts: str | None = None,
    start_cursor: str | None = None,
    page_size: int | None = None,
) -> str:
    """Query rows in a Notion data source.

    IMPORTANT: filter and sorts must be passed as JSON-encoded strings, NOT as objects.

    Args:
        data_source_id: The UUID of the data source to query.
        filter: Optional JSON string for a filter object.
        sorts: Optional JSON string for a list of sort objects.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().query_data_source(
            data_source_id,
            filter=_parse_json(filter, "filter"),
            sorts=_parse_json(sorts, "sorts"),
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def list_data_source_templates(
    data_source_id: str,
    name: str | None = None,
    start_cursor: str | None = None,
    page_size: int | None = None,
) -> str:
    """List templates for a Notion data source.

    Args:
        data_source_id: The UUID of the data source.
        name: Optional name filter for templates.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().list_data_source_templates(
            data_source_id,
            name=name,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
