"""Search tool — wraps SearchMixin method."""

from __future__ import annotations

import json

from ..server import mcp, get_client, _parse_json, _error_response


@mcp.tool()
def search(
    query: str | None = None,
    filter: str | None = None,
    sort: str | None = None,
    start_cursor: str | None = None,
    page_size: int | None = None,
) -> str:
    """Search Notion pages and databases.

    Args:
        query: Optional text query to search for.
        filter: Optional JSON string for a filter object,
            e.g. {"value": "page", "property": "object"}.
        sort: Optional JSON string for a sort object,
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
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
