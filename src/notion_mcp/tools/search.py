"""Search tool — wraps SearchMixin method."""

from __future__ import annotations

import json
from typing import Any, Annotated

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response, _slim_response


def _filter_data_source_objects(result: dict[str, Any]) -> dict[str, Any]:
    """Filter out data source objects that the v2025-09-03 API returns as databases.

    The Notion v2025-09-03 search endpoint returns data sources as separate
    objects in search results. These look like database objects (object="database")
    but their IDs are data_source_ids, not database_ids. Using these IDs with
    query_database or get_database causes 404 errors.

    Real database objects always have a ``data_sources`` key in v2025-09-03.
    Data source objects surfaced by search do NOT. This function filters them out.
    """
    if "results" not in result or not isinstance(result["results"], list):
        return result

    filtered = [
        item for item in result["results"]
        if not _is_data_source_masquerading_as_database(item)
    ]

    result = dict(result)
    result["results"] = filtered
    return result


def _is_data_source_masquerading_as_database(item: Any) -> bool:
    """Return True if a search result is a data source pretending to be a database.

    In v2025-09-03, real databases have ``object: "database"`` AND a
    ``data_sources`` key.  Data source objects surfaced by search have
    ``object: "database"`` but lack ``data_sources``.
    """
    if not isinstance(item, dict):
        return False
    return item.get("object") == "database" and "data_sources" not in item


@mcp.tool()
def search(
    query: Annotated[str | None, Field(description="Text query to search for")] = None,
    filter: Annotated[str | dict | None, Field(description="JSON string or object for a filter, e.g. {\"value\": \"page\", \"property\": \"object\"}")] = None,
    sort: Annotated[str | dict | None, Field(description="JSON string or object for a sort, e.g. {\"direction\": \"ascending\", \"timestamp\": \"last_edited_time\"}")] = None,
    start_cursor: Annotated[str | None, Field(description="Cursor for pagination")] = None,
    page_size: Annotated[int | None, Field(description="Number of results per page")] = None,
) -> str:
    """Search Notion pages and databases.

    Args:
        query: Optional text query to search for.
        filter: Optional JSON string or object for a filter,
            e.g. {"value": "page", "property": "object"}.
        sort: Optional JSON string or object for a sort,
            e.g. {"direction": "ascending", "timestamp": "last_edited_time"}.
        start_cursor: Optional cursor for pagination.
        page_size: Optional number of results per page.
    """
    try:
        result = get_client().search(
            query=query,
            filter=_parse_json(filter, "filter"),
            sort=_parse_json(sort, "sort"),
            start_cursor=start_cursor,
            page_size=page_size,
        )
        result = _filter_data_source_objects(result)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
