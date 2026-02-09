"""Database and data source tools — wraps DatabasesMixin methods."""

from __future__ import annotations

import json
from typing import Annotated, Any

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response


# ---------------------------------------------------------------------------
# Database tools
# ---------------------------------------------------------------------------


@mcp.tool()
def create_database(
    parent: Annotated[str | dict, Field(description="JSON string or object for the parent, e.g. {\"type\": \"page_id\", \"page_id\": \"...\"}")],
    title: Annotated[str | list, Field(description="JSON string or array for the title rich-text array, e.g. [{\"type\": \"text\", \"text\": {\"content\": \"My DB\"}}]")],
    initial_data_source: Annotated[str | dict | None, Field(description="JSON string or object for the initial data source configuration including properties")] = None,
    description: Annotated[str | list | None, Field(description="JSON string or array for the description rich-text array")] = None,
    is_inline: Annotated[bool | None, Field(description="If true, the database is created inline within the parent page")] = None,
    icon: Annotated[str | dict | None, Field(description="JSON string or object for the database icon, e.g. {\"type\": \"emoji\", \"emoji\": \"...\"}")] = None,
    cover: Annotated[str | dict | None, Field(description="JSON string or object for the database cover, e.g. {\"type\": \"external\", \"external\": {\"url\": \"https://...\"}}")] = None,
) -> str:
    """Create a new Notion database.

    In Notion API v2025-09-03, database properties live on data sources.
    Pass properties inside initial_data_source.properties.

    Args:
        parent: JSON string or object for the parent, e.g. {"type": "page_id", "page_id": "..."}.
        title: JSON string or array for the title rich-text array,
            e.g. [{"type": "text", "text": {"content": "My DB"}}].
        initial_data_source: Optional JSON string or object for the initial data source
            configuration including properties.
        description: Optional JSON string or array for the description rich-text array.
        is_inline: If true, the database is created inline within the parent page.
        icon: Optional JSON string or object for the database icon.
        cover: Optional JSON string or object for the database cover.
    """
    try:
        kwargs: dict[str, Any] = dict(
            parent=_parse_json(parent, "parent"),
            title=_parse_json(title, "title"),
            initial_data_source=_parse_json(initial_data_source, "initial_data_source"),
        )
        if description is not None:
            kwargs["description"] = _parse_json(description, "description")
        if is_inline is not None:
            kwargs["is_inline"] = is_inline
        if icon is not None:
            kwargs["icon"] = _parse_json(icon, "icon")
        if cover is not None:
            kwargs["cover"] = _parse_json(cover, "cover")
        result = get_client().create_database(**kwargs)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def get_database(
    database_id: Annotated[str, Field(description="The UUID of the database to retrieve")],
) -> str:
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
    database_id: Annotated[str, Field(description="The UUID of the database to update")],
    title: Annotated[str | list | None, Field(description="JSON string or array for the new title rich-text array")] = None,
    description: Annotated[str | list | None, Field(description="JSON string or array for the description rich-text array")] = None,
    icon: Annotated[str | dict | None, Field(description="JSON string or object for the database icon, e.g. {\"type\": \"emoji\", \"emoji\": \"...\"}")] = None,
    cover: Annotated[str | dict | None, Field(description="JSON string or object for the database cover, e.g. {\"type\": \"external\", \"external\": {\"url\": \"https://...\"}}")] = None,
) -> str:
    """Update a Notion database.

    Args:
        database_id: The UUID of the database to update.
        title: Optional JSON string or array for the new title rich-text array.
        description: Optional JSON string or array for the description rich-text array.
        icon: Optional JSON string or object for the database icon.
        cover: Optional JSON string or object for the database cover.
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
def archive_database(
    database_id: Annotated[str, Field(description="The UUID of the database to archive")],
) -> str:
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
    database_id: Annotated[str, Field(description="The UUID of the database to query")],
    filter: Annotated[str | dict | None, Field(description="JSON string or object for a filter, e.g. {\"property\": \"Status\", \"select\": {\"equals\": \"Done\"}}")] = None,
    sorts: Annotated[str | list | None, Field(description="JSON string or array for a list of sort objects, e.g. [{\"property\": \"Created\", \"direction\": \"descending\"}]")] = None,
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
    filter_properties: Annotated[str | list | None, Field(description="Optional list of property IDs to include in results. Pass as a JSON array of strings or a list.")] = None,
    archived: Annotated[bool | None, Field(description="If true, only return archived pages")] = None,
    in_trash: Annotated[bool | None, Field(description="If true, only return trashed pages")] = None,
) -> str:
    """Query a Notion database for pages/rows.

    Automatically resolves the first data source and queries it.
    If you already know the data source ID, use query_data_source instead.

    Args:
        database_id: The UUID of the database to query.
        filter: Optional JSON string or object for a filter.
        sorts: Optional JSON string or array for a list of sort objects.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
        filter_properties: Optional list of property IDs to include in results.
        archived: If true, only return archived pages.
        in_trash: If true, only return trashed pages.
    """
    try:
        kwargs: dict[str, Any] = dict(
            filter=_parse_json(filter, "filter"),
            sorts=_parse_json(sorts, "sorts"),
            start_cursor=start_cursor,
            page_size=page_size,
        )
        if filter_properties is not None:
            kwargs["filter_properties"] = _parse_json(filter_properties, "filter_properties")
        if archived is not None:
            kwargs["archived"] = archived
        if in_trash is not None:
            kwargs["in_trash"] = in_trash
        result = get_client().query_database(database_id, **kwargs)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


# ---------------------------------------------------------------------------
# Data source tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_data_source(
    data_source_id: Annotated[str, Field(description="The UUID of the data source to retrieve")],
) -> str:
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
    data_source_id: Annotated[str, Field(description="The UUID of the data source to update")],
    properties: Annotated[str | dict | None, Field(description="JSON string or object for properties to update")] = None,
) -> str:
    """Update a Notion data source.

    Args:
        data_source_id: The UUID of the data source to update.
        properties: Optional JSON string or object for properties to update.
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
    data_source_id: Annotated[str, Field(description="The UUID of the data source to query")],
    filter: Annotated[str | dict | None, Field(description="JSON string or object for a filter, e.g. {\"property\": \"Status\", \"select\": {\"equals\": \"Done\"}}")] = None,
    sorts: Annotated[str | list | None, Field(description="JSON string or array for a list of sort objects, e.g. [{\"property\": \"Created\", \"direction\": \"descending\"}]")] = None,
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
    filter_properties: Annotated[str | list | None, Field(description="Optional list of property IDs to include in results. Pass as a JSON array of strings or a list.")] = None,
    archived: Annotated[bool | None, Field(description="If true, only return archived pages")] = None,
    in_trash: Annotated[bool | None, Field(description="If true, only return trashed pages")] = None,
    result_type: Annotated[str | None, Field(description='Optional result type: "page" or "data_source"')] = None,
) -> str:
    """Query rows in a Notion data source.

    Args:
        data_source_id: The UUID of the data source to query.
        filter: Optional JSON string or object for a filter.
        sorts: Optional JSON string or array for a list of sort objects.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
        filter_properties: Optional list of property IDs to include in results.
        archived: If true, only return archived pages.
        in_trash: If true, only return trashed pages.
        result_type: Optional result type: "page" or "data_source".
    """
    try:
        kwargs: dict[str, Any] = dict(
            filter=_parse_json(filter, "filter"),
            sorts=_parse_json(sorts, "sorts"),
            start_cursor=start_cursor,
            page_size=page_size,
        )
        if filter_properties is not None:
            kwargs["filter_properties"] = _parse_json(filter_properties, "filter_properties")
        if archived is not None:
            kwargs["archived"] = archived
        if in_trash is not None:
            kwargs["in_trash"] = in_trash
        if result_type is not None:
            kwargs["result_type"] = result_type
        result = get_client().query_data_source(data_source_id, **kwargs)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def list_data_source_templates(
    data_source_id: Annotated[str, Field(description="The UUID of the data source")],
    name: Annotated[str | None, Field(description="Name filter for templates")] = None,
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
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
