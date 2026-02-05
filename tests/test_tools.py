"""Tests for notion-mcp tool functions.

These tests mock the NotionClient so no real API calls are made.
They verify that:
  - JSON string parameters are correctly parsed before being passed to the SDK
  - SDK methods receive the expected arguments
  - Successful responses are returned as JSON strings
  - Errors are caught and formatted properly
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def mock_client():
    """Patch get_client() to return a MagicMock for every test."""
    client = MagicMock()
    with patch("notion_mcp.server._client", None):
        with patch("notion_mcp.server.NotionClient", return_value=client):
            # Reset the global so get_client() creates a fresh mock
            import notion_mcp.server as srv
            srv._client = None
            yield client
            srv._client = None


# ---------------------------------------------------------------------------
# Page tools
# ---------------------------------------------------------------------------


class TestPageTools:
    def test_create_page(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-1", "object": "page"}
        parent = json.dumps({"type": "page_id", "page_id": "abc"})
        props = json.dumps({"title": [{"text": {"content": "Test"}}]})
        result = create_page(parent=parent, properties=props)
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.create_page.assert_called_once_with(
            parent={"type": "page_id", "page_id": "abc"},
            properties={"title": [{"text": {"content": "Test"}}]},
            children=None,
            template=None,
        )

    def test_create_page_with_children(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-2"}
        children = json.dumps([{"object": "block", "type": "paragraph"}])
        result = create_page(
            parent='{"type": "page_id", "page_id": "abc"}',
            properties='{"title": []}',
            children=children,
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-2"
        call_kwargs = mock_client.create_page.call_args
        assert call_kwargs.kwargs["children"] == [{"object": "block", "type": "paragraph"}]

    def test_get_page(self, mock_client):
        from notion_mcp.tools.pages import get_page

        mock_client.get_page.return_value = {"id": "page-1", "object": "page"}
        result = get_page("page-1")
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.get_page.assert_called_once_with("page-1")

    def test_update_page(self, mock_client):
        from notion_mcp.tools.pages import update_page

        mock_client.update_page.return_value = {"id": "page-1"}
        result = update_page(
            page_id="page-1",
            properties='{"title": [{"text": {"content": "New title"}}]}',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"

    def test_update_page_erase_content(self, mock_client):
        from notion_mcp.tools.pages import update_page

        mock_client.update_page.return_value = {"id": "page-1"}
        result = update_page(page_id="page-1", erase_content=True)
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.update_page.assert_called_once_with("page-1", erase_content=True)

    def test_archive_page(self, mock_client):
        from notion_mcp.tools.pages import archive_page

        mock_client.archive_page.return_value = {"id": "page-1", "archived": True}
        result = archive_page("page-1")
        parsed = json.loads(result)
        assert parsed["archived"] is True
        mock_client.archive_page.assert_called_once_with("page-1")

    def test_move_page(self, mock_client):
        from notion_mcp.tools.pages import move_page

        mock_client.move_page.return_value = {"id": "page-1"}
        result = move_page(
            page_id="page-1",
            parent='{"type": "page_id", "page_id": "new-parent"}',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.move_page.assert_called_once_with(
            "page-1",
            parent={"type": "page_id", "page_id": "new-parent"},
        )


# ---------------------------------------------------------------------------
# Database tools
# ---------------------------------------------------------------------------


class TestDatabaseTools:
    def test_create_database(self, mock_client):
        from notion_mcp.tools.databases import create_database

        mock_client.create_database.return_value = {"id": "db-1", "object": "database"}
        result = create_database(
            parent='{"type": "page_id", "page_id": "abc"}',
            title='[{"type": "text", "text": {"content": "My DB"}}]',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "db-1"

    def test_get_database(self, mock_client):
        from notion_mcp.tools.databases import get_database

        mock_client.get_database.return_value = {"id": "db-1"}
        result = get_database("db-1")
        parsed = json.loads(result)
        assert parsed["id"] == "db-1"

    def test_update_database(self, mock_client):
        from notion_mcp.tools.databases import update_database

        mock_client.update_database.return_value = {"id": "db-1"}
        result = update_database(
            database_id="db-1",
            title='[{"type": "text", "text": {"content": "Renamed"}}]',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "db-1"

    def test_archive_database(self, mock_client):
        from notion_mcp.tools.databases import archive_database

        mock_client.archive_database.return_value = {"id": "db-1", "archived": True}
        result = archive_database("db-1")
        parsed = json.loads(result)
        assert parsed["archived"] is True

    def test_query_database(self, mock_client):
        from notion_mcp.tools.databases import query_database

        mock_client.query_database.return_value = {"results": [], "has_more": False}
        result = query_database("db-1", page_size=10)
        parsed = json.loads(result)
        assert parsed["has_more"] is False
        mock_client.query_database.assert_called_once_with(
            "db-1", filter=None, sorts=None, start_cursor=None, page_size=10,
        )

    def test_get_data_source(self, mock_client):
        from notion_mcp.tools.databases import get_data_source

        mock_client.get_data_source.return_value = {"id": "ds-1"}
        result = get_data_source("ds-1")
        parsed = json.loads(result)
        assert parsed["id"] == "ds-1"

    def test_update_data_source(self, mock_client):
        from notion_mcp.tools.databases import update_data_source

        mock_client.update_data_source.return_value = {"id": "ds-1"}
        result = update_data_source("ds-1", properties='{"Name": {"title": {}}}')
        parsed = json.loads(result)
        assert parsed["id"] == "ds-1"

    def test_query_data_source(self, mock_client):
        from notion_mcp.tools.databases import query_data_source

        mock_client.query_data_source.return_value = {"results": []}
        result = query_data_source("ds-1")
        parsed = json.loads(result)
        assert "results" in parsed

    def test_list_data_source_templates(self, mock_client):
        from notion_mcp.tools.databases import list_data_source_templates

        mock_client.list_data_source_templates.return_value = {"results": []}
        result = list_data_source_templates("ds-1", name="Weekly")
        parsed = json.loads(result)
        assert "results" in parsed
        mock_client.list_data_source_templates.assert_called_once_with(
            "ds-1", name="Weekly", start_cursor=None, page_size=None,
        )


# ---------------------------------------------------------------------------
# Block tools
# ---------------------------------------------------------------------------


class TestBlockTools:
    def test_get_block(self, mock_client):
        from notion_mcp.tools.blocks import get_block

        mock_client.get_block.return_value = {"id": "block-1", "type": "paragraph"}
        result = get_block("block-1")
        parsed = json.loads(result)
        assert parsed["type"] == "paragraph"

    def test_get_block_children(self, mock_client):
        from notion_mcp.tools.blocks import get_block_children

        mock_client.get_block_children.return_value = {"results": [], "has_more": False}
        result = get_block_children("block-1", page_size=5)
        parsed = json.loads(result)
        assert parsed["has_more"] is False

    def test_append_block_children(self, mock_client):
        from notion_mcp.tools.blocks import append_block_children

        mock_client.append_block_children.return_value = {"results": [{"id": "new-block"}]}
        children = json.dumps([{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}])
        result = append_block_children("block-1", children=children)
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1

    def test_update_block(self, mock_client):
        from notion_mcp.tools.blocks import update_block

        mock_client.update_block.return_value = {"id": "block-1"}
        content = json.dumps({"paragraph": {"rich_text": [{"text": {"content": "updated"}}]}})
        result = update_block("block-1", content=content)
        parsed = json.loads(result)
        assert parsed["id"] == "block-1"
        mock_client.update_block.assert_called_once_with(
            "block-1",
            paragraph={"rich_text": [{"text": {"content": "updated"}}]},
        )

    def test_delete_block(self, mock_client):
        from notion_mcp.tools.blocks import delete_block

        mock_client.delete_block.return_value = {"id": "block-1", "archived": True}
        result = delete_block("block-1")
        parsed = json.loads(result)
        assert parsed["archived"] is True


# ---------------------------------------------------------------------------
# User tools
# ---------------------------------------------------------------------------


class TestUserTools:
    def test_get_users(self, mock_client):
        from notion_mcp.tools.users import get_users

        mock_client.get_users.return_value = {"results": [{"id": "user-1"}]}
        result = get_users()
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1

    def test_get_self(self, mock_client):
        from notion_mcp.tools.users import get_self

        mock_client.get_self.return_value = {"id": "bot-1", "type": "bot"}
        result = get_self()
        parsed = json.loads(result)
        assert parsed["type"] == "bot"


# ---------------------------------------------------------------------------
# Comment tools
# ---------------------------------------------------------------------------


class TestCommentTools:
    def test_create_comment(self, mock_client):
        from notion_mcp.tools.comments import create_comment

        mock_client.create_comment.return_value = {"id": "comment-1"}
        result = create_comment(
            parent='{"page_id": "page-1"}',
            rich_text='[{"type": "text", "text": {"content": "Nice!"}}]',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "comment-1"
        mock_client.create_comment.assert_called_once_with(
            parent={"page_id": "page-1"},
            rich_text=[{"type": "text", "text": {"content": "Nice!"}}],
        )

    def test_get_comments(self, mock_client):
        from notion_mcp.tools.comments import get_comments

        mock_client.get_comments.return_value = {"results": []}
        result = get_comments("block-1", page_size=10)
        parsed = json.loads(result)
        assert "results" in parsed


# ---------------------------------------------------------------------------
# Search tool
# ---------------------------------------------------------------------------


class TestSearchTool:
    def test_search_basic(self, mock_client):
        from notion_mcp.tools.search import search

        mock_client.search.return_value = {"results": [], "has_more": False}
        result = search(query="meeting notes")
        parsed = json.loads(result)
        assert parsed["has_more"] is False
        mock_client.search.assert_called_once_with(
            query="meeting notes",
            filter=None,
            sort=None,
            start_cursor=None,
            page_size=None,
        )

    def test_search_with_filter(self, mock_client):
        from notion_mcp.tools.search import search

        mock_client.search.return_value = {"results": [{"id": "page-1"}]}
        result = search(
            query="project",
            filter='{"value": "page", "property": "object"}',
            sort='{"direction": "descending", "timestamp": "last_edited_time"}',
            page_size=5,
        )
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1
        mock_client.search.assert_called_once_with(
            query="project",
            filter={"value": "page", "property": "object"},
            sort={"direction": "descending", "timestamp": "last_edited_time"},
            start_cursor=None,
            page_size=5,
        )


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_invalid_json_parameter(self, mock_client):
        from notion_mcp.tools.pages import create_page

        result = create_page(parent="not valid json{{{", properties="{}")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "Invalid JSON" in parsed["message"]

    def test_sdk_exception(self, mock_client):
        from notion_mcp.tools.pages import get_page

        mock_client.get_page.side_effect = RuntimeError("Connection failed")
        result = get_page("page-1")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert "Connection failed" in parsed["message"]


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_parse_json_string(self):
        from notion_mcp.server import _parse_json

        assert _parse_json('{"a": 1}', "test") == {"a": 1}

    def test_parse_json_dict_passthrough(self):
        from notion_mcp.server import _parse_json

        d = {"a": 1}
        assert _parse_json(d, "test") is d

    def test_parse_json_list_passthrough(self):
        from notion_mcp.server import _parse_json

        lst = [1, 2, 3]
        assert _parse_json(lst, "test") is lst

    def test_parse_json_none(self):
        from notion_mcp.server import _parse_json

        assert _parse_json(None, "test") is None

    def test_parse_json_invalid(self):
        from notion_mcp.server import _parse_json

        with pytest.raises(ValueError, match="Invalid JSON"):
            _parse_json("{bad", "test_param")
