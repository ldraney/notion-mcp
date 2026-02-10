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

import httpx
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
        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["parent"] == {"type": "page_id", "page_id": "abc"}
        assert call_kwargs["properties"] == {"title": [{"text": {"content": "Test"}}]}
        assert call_kwargs["children"] is None
        assert call_kwargs["template"] is None
        # position, icon, cover should NOT be passed when not set
        assert "position" not in call_kwargs
        assert "icon" not in call_kwargs
        assert "cover" not in call_kwargs

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

    def test_create_page_with_template(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-3"}
        template = json.dumps({"type": "template_id", "template_id": "tmpl-abc"})
        result = create_page(
            parent='{"type": "page_id", "page_id": "abc"}',
            properties='{"title": []}',
            template=template,
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-3"
        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["parent"] == {"type": "page_id", "page_id": "abc"}
        assert call_kwargs["properties"] == {"title": []}
        assert call_kwargs["children"] is None
        assert call_kwargs["template"] == {"type": "template_id", "template_id": "tmpl-abc"}

    def test_create_page_with_position_icon_cover(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-4"}
        result = create_page(
            parent='{"type": "page_id", "page_id": "abc"}',
            properties='{"title": []}',
            position='{"type": "page_start"}',
            icon='{"type": "emoji", "emoji": "X"}',
            cover='{"type": "external", "external": {"url": "https://example.com"}}',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-4"
        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["position"] == {"type": "page_start"}
        assert call_kwargs["icon"] == {"type": "emoji", "emoji": "X"}
        assert call_kwargs["cover"] == {"type": "external", "external": {"url": "https://example.com"}}

    def test_get_page(self, mock_client):
        from notion_mcp.tools.pages import get_page

        mock_client.get_page.return_value = {"id": "page-1", "object": "page"}
        result = get_page("page-1")
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.get_page.assert_called_once_with("page-1")

    def test_get_page_with_filter_properties(self, mock_client):
        from notion_mcp.tools.pages import get_page

        mock_client.get_page.return_value = {"id": "page-1", "object": "page"}
        result = get_page("page-1", filter_properties='["title", "status"]')
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.get_page.assert_called_once_with(
            "page-1", filter_properties=["title", "status"],
        )

    def test_get_page_property_item(self, mock_client):
        from notion_mcp.tools.pages import get_page_property_item

        mock_client.get_page_property_item.return_value = {
            "object": "property_item",
            "type": "title",
            "title": {"text": {"content": "Test"}},
        }
        result = get_page_property_item("page-1", "prop-abc")
        parsed = json.loads(result)
        assert parsed["type"] == "title"
        mock_client.get_page_property_item.assert_called_once_with(
            "page-1", "prop-abc", start_cursor=None, page_size=None,
        )

    def test_get_page_property_item_paginated(self, mock_client):
        from notion_mcp.tools.pages import get_page_property_item

        mock_client.get_page_property_item.return_value = {
            "object": "list",
            "results": [{"id": "r1"}],
            "has_more": True,
            "next_cursor": "cursor-abc",
        }
        result = get_page_property_item(
            "page-1", "prop-abc", start_cursor="cursor-prev", page_size=5,
        )
        parsed = json.loads(result)
        assert parsed["has_more"] is True
        mock_client.get_page_property_item.assert_called_once_with(
            "page-1", "prop-abc", start_cursor="cursor-prev", page_size=5,
        )

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

    def test_update_page_erase_content_with_properties(self, mock_client):
        """erase_content and properties can be combined in one call."""
        from notion_mcp.tools.pages import update_page

        mock_client.update_page.return_value = {"id": "page-1"}
        result = update_page(
            page_id="page-1",
            properties='{"title": [{"text": {"content": "Cleared"}}]}',
            erase_content=True,
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.update_page.assert_called_once_with(
            "page-1",
            erase_content=True,
            properties={"title": [{"text": {"content": "Cleared"}}]},
        )

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

    def test_create_database_with_new_params(self, mock_client):
        from notion_mcp.tools.databases import create_database

        mock_client.create_database.return_value = {"id": "db-new"}
        result = create_database(
            parent='{"type": "page_id", "page_id": "abc"}',
            title='[{"type": "text", "text": {"content": "My DB"}}]',
            description='[{"type": "text", "text": {"content": "A description"}}]',
            is_inline=True,
            icon='{"type": "emoji", "emoji": "X"}',
            cover='{"type": "external", "external": {"url": "https://example.com"}}',
        )
        parsed = json.loads(result)
        assert parsed["id"] == "db-new"
        call_kwargs = mock_client.create_database.call_args.kwargs
        assert call_kwargs["description"] == [{"type": "text", "text": {"content": "A description"}}]
        assert call_kwargs["is_inline"] is True
        assert call_kwargs["icon"] == {"type": "emoji", "emoji": "X"}
        assert call_kwargs["cover"] == {"type": "external", "external": {"url": "https://example.com"}}

    def test_query_database(self, mock_client):
        from notion_mcp.tools.databases import query_database

        mock_client.query_database.return_value = {"results": [], "has_more": False}
        result = query_database("db-1", page_size=10)
        parsed = json.loads(result)
        assert parsed["has_more"] is False
        mock_client.query_database.assert_called_once_with(
            "db-1", filter=None, sorts=None, start_cursor=None, page_size=10,
        )

    def test_query_database_with_new_params(self, mock_client):
        from notion_mcp.tools.databases import query_database

        mock_client.query_database.return_value = {"results": [], "has_more": False}
        result = query_database(
            "db-1",
            filter_properties='["title", "status"]',
            archived=True,
            in_trash=False,
        )
        parsed = json.loads(result)
        assert parsed["has_more"] is False
        mock_client.query_database.assert_called_once_with(
            "db-1",
            filter=None,
            sorts=None,
            start_cursor=None,
            page_size=None,
            filter_properties=["title", "status"],
            archived=True,
            in_trash=False,
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

    def test_query_data_source_with_new_params(self, mock_client):
        from notion_mcp.tools.databases import query_data_source

        mock_client.query_data_source.return_value = {"results": [], "has_more": False}
        result = query_data_source(
            "ds-1",
            filter_properties='["title"]',
            archived=True,
            in_trash=False,
            result_type="page",
        )
        parsed = json.loads(result)
        assert "results" in parsed
        mock_client.query_data_source.assert_called_once_with(
            "ds-1",
            filter=None,
            sorts=None,
            start_cursor=None,
            page_size=None,
            filter_properties=["title"],
            archived=True,
            in_trash=False,
            result_type="page",
        )

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
        mock_client.append_block_children.assert_called_once_with(
            "block-1",
            children=[{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}],
            position=None,
        )

    def test_append_block_children_with_position(self, mock_client):
        from notion_mcp.tools.blocks import append_block_children

        mock_client.append_block_children.return_value = {"results": [{"id": "new-block"}]}
        children = json.dumps([{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}])
        position = json.dumps({"type": "start"})
        result = append_block_children("block-1", children=children, position=position)
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1
        mock_client.append_block_children.assert_called_once_with(
            "block-1",
            children=[{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}],
            position={"type": "start"},
        )

    def test_append_block_children_with_after_block_position(self, mock_client):
        from notion_mcp.tools.blocks import append_block_children

        mock_client.append_block_children.return_value = {"results": [{"id": "new-block"}]}
        children = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}]
        position = {"type": "after_block", "after_block": {"id": "target-block"}}
        result = append_block_children("block-1", children=children, position=position)
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1
        mock_client.append_block_children.assert_called_once_with(
            "block-1",
            children=children,
            position=position,
        )

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

    def test_get_user(self, mock_client):
        from notion_mcp.tools.users import get_user

        mock_client.get_user.return_value = {"id": "user-1", "type": "person", "name": "Alice"}
        result = get_user("user-1")
        parsed = json.loads(result)
        assert parsed["id"] == "user-1"
        assert parsed["type"] == "person"
        mock_client.get_user.assert_called_once_with("user-1")

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

    def test_create_comment_with_discussion_id(self, mock_client):
        from notion_mcp.tools.comments import create_comment

        mock_client.create_comment.return_value = {"id": "comment-2"}
        result = create_comment(
            parent='{"page_id": "page-1"}',
            rich_text='[{"type": "text", "text": {"content": "Reply!"}}]',
            discussion_id="disc-abc",
        )
        parsed = json.loads(result)
        assert parsed["id"] == "comment-2"
        mock_client.create_comment.assert_called_once_with(
            parent={"page_id": "page-1"},
            rich_text=[{"type": "text", "text": {"content": "Reply!"}}],
            discussion_id="disc-abc",
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

    def test_search_filters_out_data_source_objects(self, mock_client):
        """Data source objects masquerading as databases should be filtered out.

        The Notion v2025-09-03 search endpoint returns data sources as separate
        objects with object="database" but without a "data_sources" key.
        These cause 404 errors when used with query_database/get_database.
        """
        from notion_mcp.tools.search import search

        # A real database has object="database" AND data_sources
        real_database = {
            "object": "database",
            "id": "db-real-123",
            "title": [{"type": "text", "text": {"content": "Real DB"}}],
            "data_sources": [{"id": "ds-abc", "type": "default"}],
            "parent": {"type": "workspace", "workspace": True},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
        }
        # A data source masquerading as a database has object="database" but NO data_sources
        fake_database = {
            "object": "database",
            "id": "ds-fake-456",
            "title": [{"type": "text", "text": {"content": "Fake DB (data source)"}}],
            "properties": {
                "Name": {"id": "title", "type": "title", "title": {}},
                "Status": {"id": "s1", "type": "select", "select": {"options": []}},
            },
            "parent": {"type": "page_id", "page_id": "page-parent"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
        }
        # A page should never be filtered
        page = {
            "object": "page",
            "id": "page-789",
            "properties": {"Name": {"id": "title", "type": "title", "title": []}},
            "parent": {"type": "database_id", "database_id": "db-real-123"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
        }

        mock_client.search.return_value = {
            "object": "list",
            "results": [real_database, fake_database, page],
            "has_more": False,
            "next_cursor": None,
        }

        result = search(query="test")
        parsed = json.loads(result)

        # Should have 2 results: the real database and the page (fake filtered out)
        assert len(parsed["results"]) == 2
        result_ids = [r["id"] for r in parsed["results"]]
        assert "db-real-123" in result_ids
        assert "page-789" in result_ids
        assert "ds-fake-456" not in result_ids

    def test_search_keeps_all_pages(self, mock_client):
        """Pages should never be filtered, even if they lack data_sources."""
        from notion_mcp.tools.search import search

        page1 = {
            "object": "page",
            "id": "page-1",
            "properties": {},
            "parent": {"type": "workspace"},
        }
        page2 = {
            "object": "page",
            "id": "page-2",
            "properties": {},
            "parent": {"type": "workspace"},
        }
        mock_client.search.return_value = {
            "object": "list",
            "results": [page1, page2],
            "has_more": False,
        }

        result = search(query="test")
        parsed = json.loads(result)
        assert len(parsed["results"]) == 2

    def test_search_keeps_real_databases(self, mock_client):
        """Real databases (with data_sources) should be kept."""
        from notion_mcp.tools.search import search

        real_db = {
            "object": "database",
            "id": "db-1",
            "title": [{"type": "text", "text": {"content": "DB"}}],
            "data_sources": [{"id": "ds-1", "type": "default"}],
        }
        mock_client.search.return_value = {
            "object": "list",
            "results": [real_db],
            "has_more": False,
        }

        result = search(query="test")
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1
        assert parsed["results"][0]["id"] == "db-1"


# ---------------------------------------------------------------------------
# Data source filtering helpers (unit tests)
# ---------------------------------------------------------------------------


class TestDataSourceFiltering:
    """Unit tests for _filter_data_source_objects and _is_data_source_masquerading_as_database."""

    def test_is_data_source_masquerading_true(self):
        from notion_mcp.tools.search import _is_data_source_masquerading_as_database

        item = {"object": "database", "id": "ds-1", "properties": {}}
        assert _is_data_source_masquerading_as_database(item) is True

    def test_is_data_source_masquerading_false_for_real_db(self):
        from notion_mcp.tools.search import _is_data_source_masquerading_as_database

        item = {"object": "database", "id": "db-1", "data_sources": [{"id": "ds-1"}]}
        assert _is_data_source_masquerading_as_database(item) is False

    def test_is_data_source_masquerading_false_for_page(self):
        from notion_mcp.tools.search import _is_data_source_masquerading_as_database

        item = {"object": "page", "id": "page-1", "properties": {}}
        assert _is_data_source_masquerading_as_database(item) is False

    def test_is_data_source_masquerading_false_for_non_dict(self):
        from notion_mcp.tools.search import _is_data_source_masquerading_as_database

        assert _is_data_source_masquerading_as_database("not a dict") is False
        assert _is_data_source_masquerading_as_database(42) is False
        assert _is_data_source_masquerading_as_database(None) is False

    def test_filter_no_results_key(self):
        from notion_mcp.tools.search import _filter_data_source_objects

        data = {"has_more": False}
        assert _filter_data_source_objects(data) == {"has_more": False}

    def test_filter_empty_results(self):
        from notion_mcp.tools.search import _filter_data_source_objects

        data = {"results": [], "has_more": False}
        result = _filter_data_source_objects(data)
        assert result["results"] == []

    def test_filter_removes_fake_databases(self):
        from notion_mcp.tools.search import _filter_data_source_objects

        data = {
            "results": [
                {"object": "database", "id": "db-1", "data_sources": [{"id": "ds-1"}]},
                {"object": "database", "id": "ds-fake", "properties": {}},
                {"object": "page", "id": "page-1"},
            ],
            "has_more": False,
        }
        result = _filter_data_source_objects(data)
        assert len(result["results"]) == 2
        assert result["results"][0]["id"] == "db-1"
        assert result["results"][1]["id"] == "page-1"

    def test_filter_does_not_mutate_original(self):
        from notion_mcp.tools.search import _filter_data_source_objects

        original_results = [
            {"object": "database", "id": "ds-fake", "properties": {}},
            {"object": "page", "id": "page-1"},
        ]
        data = {"results": original_results, "has_more": False}
        result = _filter_data_source_objects(data)
        # Original data should still have 2 results
        assert len(data["results"]) == 2
        # Filtered result should have 1
        assert len(result["results"]) == 1


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

    def test_http_status_error_json_body(self, mock_client):
        """HTTPStatusError from Notion should include status_code and API error details."""
        from notion_mcp.tools.pages import get_page

        response = httpx.Response(
            status_code=404,
            json={"object": "error", "code": "object_not_found", "message": "Page not found"},
            request=httpx.Request("GET", "https://api.notion.com/v1/pages/page-1"),
        )
        mock_client.get_page.side_effect = httpx.HTTPStatusError(
            "Not Found", request=response.request, response=response,
        )
        result = get_page("page-1")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert parsed["status_code"] == 404
        assert "Not Found" in parsed["message"]
        assert parsed["details"]["code"] == "object_not_found"
        assert parsed["details"]["message"] == "Page not found"

    def test_http_status_error_plain_text_body(self, mock_client):
        """HTTPStatusError with non-JSON body falls back to text."""
        from notion_mcp.tools.pages import get_page

        response = httpx.Response(
            status_code=502,
            text="Bad Gateway",
            request=httpx.Request("GET", "https://api.notion.com/v1/pages/page-1"),
        )
        mock_client.get_page.side_effect = httpx.HTTPStatusError(
            "Bad Gateway", request=response.request, response=response,
        )
        result = get_page("page-1")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert parsed["status_code"] == 502
        assert parsed["details"] == "Bad Gateway"

    def test_http_status_error_rate_limit(self, mock_client):
        """HTTPStatusError for 429 rate-limit responses."""
        from notion_mcp.tools.databases import query_database

        response = httpx.Response(
            status_code=429,
            json={"object": "error", "code": "rate_limited", "message": "Rate limited"},
            request=httpx.Request("POST", "https://api.notion.com/v1/databases/db-1/query"),
        )
        mock_client.query_database.side_effect = httpx.HTTPStatusError(
            "Rate Limited", request=response.request, response=response,
        )
        result = query_database("db-1")
        parsed = json.loads(result)
        assert parsed["error"] is True
        assert parsed["status_code"] == 429
        assert parsed["details"]["code"] == "rate_limited"


# ---------------------------------------------------------------------------
# Raw dict/list parameter tests (no JSON string encoding)
# ---------------------------------------------------------------------------


class TestRawDictParams:
    """Verify that passing native dicts/lists (not JSON strings) works.

    LLMs often send raw objects instead of JSON-encoded strings.  The widened
    type annotations (str | dict, str | list, etc.) let pydantic accept them,
    and _parse_json already passes them through unchanged.
    """

    def test_create_page_raw_dict(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-raw"}
        result = create_page(
            parent={"type": "page_id", "page_id": "abc"},
            properties={"title": [{"text": {"content": "Raw"}}]},
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-raw"
        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["parent"] == {"type": "page_id", "page_id": "abc"}
        assert call_kwargs["properties"] == {"title": [{"text": {"content": "Raw"}}]}
        assert call_kwargs["children"] is None
        assert call_kwargs["template"] is None

    def test_create_page_raw_children_list(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-ch"}
        children = [{"object": "block", "type": "paragraph"}]
        result = create_page(
            parent={"type": "page_id", "page_id": "abc"},
            properties={"title": []},
            children=children,
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-ch"
        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["children"] == children

    def test_create_page_raw_template_dict(self, mock_client):
        from notion_mcp.tools.pages import create_page

        mock_client.create_page.return_value = {"id": "page-tmpl"}
        template = {"type": "template_id", "template_id": "tmpl-abc"}
        result = create_page(
            parent={"type": "page_id", "page_id": "abc"},
            properties={"title": []},
            template=template,
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-tmpl"
        call_kwargs = mock_client.create_page.call_args.kwargs
        assert call_kwargs["parent"] == {"type": "page_id", "page_id": "abc"}
        assert call_kwargs["properties"] == {"title": []}
        assert call_kwargs["children"] is None
        assert call_kwargs["template"] == template

    def test_update_page_raw_dicts(self, mock_client):
        from notion_mcp.tools.pages import update_page

        mock_client.update_page.return_value = {"id": "page-1"}
        result = update_page(
            page_id="page-1",
            properties={"title": [{"text": {"content": "New"}}]},
            icon={"type": "emoji", "emoji": "X"},
            cover={"type": "external", "external": {"url": "https://example.com"}},
        )
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.update_page.assert_called_once_with(
            "page-1",
            erase_content=None,
            properties={"title": [{"text": {"content": "New"}}]},
            icon={"type": "emoji", "emoji": "X"},
            cover={"type": "external", "external": {"url": "https://example.com"}},
        )

    def test_move_page_raw_dict(self, mock_client):
        from notion_mcp.tools.pages import move_page

        mock_client.move_page.return_value = {"id": "page-1"}
        parent = {"type": "page_id", "page_id": "new-parent"}
        result = move_page(page_id="page-1", parent=parent)
        parsed = json.loads(result)
        assert parsed["id"] == "page-1"
        mock_client.move_page.assert_called_once_with("page-1", parent=parent)

    def test_create_database_raw(self, mock_client):
        from notion_mcp.tools.databases import create_database

        mock_client.create_database.return_value = {"id": "db-raw"}
        result = create_database(
            parent={"type": "page_id", "page_id": "abc"},
            title=[{"type": "text", "text": {"content": "My DB"}}],
            initial_data_source={"properties": {"Name": {"title": {}}}},
        )
        parsed = json.loads(result)
        assert parsed["id"] == "db-raw"
        call_kwargs = mock_client.create_database.call_args.kwargs
        assert call_kwargs["parent"] == {"type": "page_id", "page_id": "abc"}
        assert call_kwargs["title"] == [{"type": "text", "text": {"content": "My DB"}}]
        assert call_kwargs["initial_data_source"] == {"properties": {"Name": {"title": {}}}}
        # Optional params not passed
        assert "description" not in call_kwargs
        assert "is_inline" not in call_kwargs
        assert "icon" not in call_kwargs
        assert "cover" not in call_kwargs

    def test_update_database_raw(self, mock_client):
        from notion_mcp.tools.databases import update_database

        mock_client.update_database.return_value = {"id": "db-1"}
        result = update_database(
            database_id="db-1",
            title=[{"type": "text", "text": {"content": "Renamed"}}],
            description=[{"type": "text", "text": {"content": "Desc"}}],
            icon={"type": "emoji", "emoji": "X"},
            cover={"type": "external", "external": {"url": "https://x.com"}},
        )
        parsed = json.loads(result)
        assert parsed["id"] == "db-1"

    def test_query_database_raw(self, mock_client):
        from notion_mcp.tools.databases import query_database

        mock_client.query_database.return_value = {"results": [], "has_more": False}
        filter_obj = {"property": "Status", "select": {"equals": "Done"}}
        sorts_obj = [{"property": "Created", "direction": "descending"}]
        result = query_database("db-1", filter=filter_obj, sorts=sorts_obj)
        parsed = json.loads(result)
        assert parsed["has_more"] is False
        call_kwargs = mock_client.query_database.call_args.kwargs
        assert call_kwargs["filter"] == filter_obj
        assert call_kwargs["sorts"] == sorts_obj

    def test_update_data_source_raw(self, mock_client):
        from notion_mcp.tools.databases import update_data_source

        mock_client.update_data_source.return_value = {"id": "ds-1"}
        props = {"Name": {"title": {}}}
        result = update_data_source("ds-1", properties=props)
        parsed = json.loads(result)
        assert parsed["id"] == "ds-1"

    def test_query_data_source_raw(self, mock_client):
        from notion_mcp.tools.databases import query_data_source

        mock_client.query_data_source.return_value = {"results": []}
        filter_obj = {"property": "Done", "checkbox": {"equals": True}}
        sorts_obj = [{"property": "Name", "direction": "ascending"}]
        result = query_data_source("ds-1", filter=filter_obj, sorts=sorts_obj)
        parsed = json.loads(result)
        assert "results" in parsed

    def test_append_block_children_raw(self, mock_client):
        from notion_mcp.tools.blocks import append_block_children

        mock_client.append_block_children.return_value = {"results": [{"id": "b1"}]}
        children = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}]
        result = append_block_children("block-1", children=children)
        parsed = json.loads(result)
        assert len(parsed["results"]) == 1
        mock_client.append_block_children.assert_called_once_with(
            "block-1", children=children, position=None,
        )

    def test_update_block_raw(self, mock_client):
        from notion_mcp.tools.blocks import update_block

        mock_client.update_block.return_value = {"id": "block-1"}
        content = {"paragraph": {"rich_text": [{"text": {"content": "updated"}}]}}
        result = update_block("block-1", content=content)
        parsed = json.loads(result)
        assert parsed["id"] == "block-1"
        mock_client.update_block.assert_called_once_with(
            "block-1",
            paragraph={"rich_text": [{"text": {"content": "updated"}}]},
        )

    def test_create_comment_raw(self, mock_client):
        from notion_mcp.tools.comments import create_comment

        mock_client.create_comment.return_value = {"id": "comment-raw"}
        result = create_comment(
            parent={"page_id": "page-1"},
            rich_text=[{"type": "text", "text": {"content": "Nice!"}}],
        )
        parsed = json.loads(result)
        assert parsed["id"] == "comment-raw"
        mock_client.create_comment.assert_called_once_with(
            parent={"page_id": "page-1"},
            rich_text=[{"type": "text", "text": {"content": "Nice!"}}],
        )

    def test_search_raw(self, mock_client):
        from notion_mcp.tools.search import search

        mock_client.search.return_value = {"results": [], "has_more": False}
        filter_obj = {"value": "page", "property": "object"}
        sort_obj = {"direction": "ascending", "timestamp": "last_edited_time"}
        result = search(query="test", filter=filter_obj, sort=sort_obj)
        parsed = json.loads(result)
        assert parsed["has_more"] is False
        mock_client.search.assert_called_once_with(
            query="test",
            filter=filter_obj,
            sort=sort_obj,
            start_cursor=None,
            page_size=None,
        )


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
