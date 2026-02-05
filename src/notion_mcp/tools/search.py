"""Search tool — wraps SearchMixin method."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _parse_json, _error_response


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
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
