"""MCP server entry point — FastMCP app and NotionClient lifecycle."""

from __future__ import annotations

import json
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from notion_sdk import NotionClient

mcp = FastMCP("notion")

# ---------------------------------------------------------------------------
# Shared client instance
# ---------------------------------------------------------------------------

_client: NotionClient | None = None


def get_client() -> NotionClient:
    """Return the shared NotionClient, creating it on first call.

    The client reads NOTION_API_KEY from the environment (via the SDK).
    """
    global _client
    if _client is None:
        _client = NotionClient()
    return _client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json(value: str | dict | list | None, name: str) -> Any:
    """Parse a JSON string into a Python object, or pass through if already parsed."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for parameter '{name}': {exc}") from exc


def _error_response(exc: Exception) -> str:
    """Format an exception into a user-friendly error string."""
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            body = exc.response.json()
        except Exception:
            body = exc.response.text
        return json.dumps(
            {
                "error": True,
                "status_code": exc.response.status_code,
                "message": str(exc),
                "details": body,
            },
            indent=2,
        )
    return json.dumps({"error": True, "message": str(exc)}, indent=2)


# ---------------------------------------------------------------------------
# Response slimming — strip Notion API metadata noise to reduce token usage
# ---------------------------------------------------------------------------

# "object" is always inferrable from context (pages have properties, blocks have type-specific content, etc.)
_ALWAYS_STRIP_KEYS = {"object", "request_id"}

# Keys stripped from page/block objects (dicts that have both "id" and "type")
_PAGE_BLOCK_STRIP_KEYS = {"parent", "created_by", "last_edited_by", "created_time", "last_edited_time"}

# Default annotations for rich_text items
_DEFAULT_ANNOTATIONS = {
    "bold": False,
    "italic": False,
    "strikethrough": False,
    "underline": False,
    "code": False,
    "color": "default",
}

# Keys whose list values contain rich_text items
_RICH_TEXT_ARRAY_KEYS = {"rich_text", "title", "caption", "description"}


def _slim_response(data: Any) -> Any:
    """Recursively strip metadata noise from a Notion API response.

    Removes null values, redundant keys, default flags, and other noise
    that inflates token usage without adding information value.
    """
    if isinstance(data, list):
        return [_slim_response(item) for item in data]

    if not isinstance(data, dict):
        return data

    result: dict[str, Any] = {}

    for key, value in data.items():
        # --- Strip null values everywhere ---
        if value is None:
            continue

        # --- Strip keys removed from ALL objects ---
        if key in _ALWAYS_STRIP_KEYS:
            continue

        # --- Strip empty type containers in list responses ---
        if key in ("block", "page_or_data_source") and isinstance(value, dict) and not value:
            continue

        # --- Handle rich_text / title / caption / description arrays ---
        if key in _RICH_TEXT_ARRAY_KEYS and isinstance(value, list):
            result[key] = [_slim_rich_text_item(item) for item in value]
            continue

        # --- Handle select values (strip id, keep name + color) ---
        if key == "select" and isinstance(value, dict) and "name" in value:
            result[key] = _slim_response(_strip_select_id(value))
            continue

        # --- Handle status values (same structure as select) ---
        if key == "status" and isinstance(value, dict) and "name" in value:
            result[key] = _slim_response(_strip_select_id(value))
            continue

        # --- Handle multi_select arrays ---
        if key == "multi_select" and isinstance(value, list):
            result[key] = [_slim_response(_strip_select_id(item)) if isinstance(item, dict) else item for item in value]
            continue

        # --- Recurse into nested structures ---
        value = _slim_response(value)

        # --- Strip block content defaults ---
        # color: "default" in block content is noise. Annotation colors are handled separately in _slim_rich_text_item.
        if key == "color" and value == "default":
            continue
        if key == "is_toggleable" and value is False:
            continue

        result[key] = value

    # --- Strip page/block metadata (dicts with both "id" and "type") ---
    if "id" in result and "type" in result:
        type_val = result.get("type")
        for mk in _PAGE_BLOCK_STRIP_KEYS:
            if mk != type_val:
                result.pop(mk, None)
        # Strip false-valued flags
        if result.get("archived") is False:
            del result["archived"]
        if result.get("in_trash") is False:
            del result["in_trash"]
        if result.get("is_locked") is False:
            del result["is_locked"]

    # --- Strip "type" from top-level list responses ---
    if "results" in result and "has_more" in result:
        result.pop("type", None)

    return result


def _slim_rich_text_item(item: Any) -> Any:
    """Slim a single rich_text item dict.

    For type: "text" items, plain_text and href are stripped because they're
    redundant with text.content and text.link respectively. For type: "mention"
    and "equation" items, plain_text and href are preserved because they contain
    the only human-readable representation of the content.
    """
    if not isinstance(item, dict):
        return _slim_response(item)

    slimmed: dict[str, Any] = {}

    for key, value in item.items():
        # Skip null values
        if value is None:
            continue
        # Only strip plain_text for text-type items (where text.content is equivalent)
        if key == "plain_text" and item.get("type") == "text":
            continue
        # Only strip href for text-type items (where text.link covers it)
        if key == "href" and item.get("type") == "text":
            continue
        # Handle annotations
        if key == "annotations" and isinstance(value, dict):
            non_defaults = {
                k: v for k, v in value.items()
                if _DEFAULT_ANNOTATIONS.get(k) != v
            }
            if non_defaults:
                slimmed["annotations"] = non_defaults
            continue
        # Handle text object — strip text.link when null
        if key == "text" and isinstance(value, dict):
            text_slimmed = {k: v for k, v in value.items() if v is not None}
            slimmed[key] = _slim_response(text_slimmed)
            continue
        # Recurse for everything else
        slimmed[key] = _slim_response(value)

    return slimmed


def _strip_select_id(value: dict) -> dict:
    """Strip 'id' from a select/multi_select/status option dict."""
    return {k: v for k, v in value.items() if k != "id"}


# ---------------------------------------------------------------------------
# Register tool modules — each module calls @mcp.tool() at import time
# ---------------------------------------------------------------------------

from .tools import register_all_tools  # noqa: E402

register_all_tools()


def main() -> None:
    """Entry point for the console script."""
    mcp.run()
