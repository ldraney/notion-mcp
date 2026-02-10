"""Tests for _slim_response — verifies metadata noise stripping."""

from __future__ import annotations

from notion_mcp.server import _slim_response


class TestNullStripping:
    def test_null_values_stripped(self):
        data = {"id": "abc", "cover": None, "icon": None, "public_url": None, "title": "Hello"}
        result = _slim_response(data)
        assert "cover" not in result
        assert "icon" not in result
        assert "public_url" not in result
        assert result["title"] == "Hello"

    def test_non_null_values_kept(self):
        data = {"id": "abc", "cover": {"url": "https://example.com"}, "title": "Hello"}
        result = _slim_response(data)
        assert "cover" in result
        assert result["title"] == "Hello"


class TestAlwaysStrippedKeys:
    def test_object_key_stripped(self):
        data = {"object": "page", "id": "abc"}
        result = _slim_response(data)
        assert "object" not in result

    def test_request_id_stripped(self):
        data = {"request_id": "req-123", "results": []}
        result = _slim_response(data)
        assert "request_id" not in result


class TestPageBlockMetadata:
    def test_page_metadata_stripped(self):
        """Page/block objects (with id + type) have metadata stripped."""
        data = {
            "id": "page-1",
            "type": "page",
            "parent": {"type": "workspace", "workspace": True},
            "created_by": {"object": "user", "id": "user-1"},
            "last_edited_by": {"object": "user", "id": "user-1"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "archived": False,
            "in_trash": False,
            "url": "https://notion.so/page-1",
        }
        result = _slim_response(data)
        assert result == {
            "id": "page-1",
            "type": "page",
            "url": "https://notion.so/page-1",
        }

    def test_archived_true_kept(self):
        data = {"id": "p1", "type": "page", "archived": True}
        result = _slim_response(data)
        assert result["archived"] is True

    def test_archived_false_stripped(self):
        data = {"id": "p1", "type": "page", "archived": False}
        result = _slim_response(data)
        assert "archived" not in result

    def test_in_trash_true_kept(self):
        data = {"id": "p1", "type": "page", "in_trash": True}
        result = _slim_response(data)
        assert result["in_trash"] is True

    def test_is_locked_false_stripped(self):
        data = {"id": "p1", "type": "page", "is_locked": False}
        result = _slim_response(data)
        assert "is_locked" not in result

    def test_is_locked_true_kept(self):
        data = {"id": "p1", "type": "page", "is_locked": True}
        result = _slim_response(data)
        assert result["is_locked"] is True

    def test_dict_without_id_and_type_not_stripped(self):
        """Dicts that lack id+type should NOT have page/block metadata stripped."""
        data = {"parent": {"type": "workspace"}, "created_time": "2024-01-01"}
        result = _slim_response(data)
        assert "parent" in result
        assert "created_time" in result



class TestPageWithoutTypeKey:
    """Pages from Notion API v2025-09-03 may not have a top-level 'type' key.
    The heuristic should still match them via 'id' + 'properties'."""

    def test_page_without_type_key_stripped(self):
        page = {
            "id": "page-1",
            "properties": {
                "Name": {"id": "title", "type": "title", "title": [{"type": "text", "text": {"content": "Test"}}]}
            },
            "parent": {"type": "database_id", "database_id": "db-1"},
            "created_by": {"object": "user", "id": "u1"},
            "last_edited_by": {"object": "user", "id": "u1"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
            "archived": False,
            "in_trash": False,
            "is_locked": False,
            "url": "https://notion.so/page-1",
        }
        result = _slim_response(page)
        assert "parent" not in result
        assert "created_by" not in result
        assert "last_edited_by" not in result
        assert "created_time" not in result
        assert "last_edited_time" not in result
        assert "archived" not in result
        assert "in_trash" not in result
        assert "is_locked" not in result
        assert result["id"] == "page-1"
        assert "properties" in result
        assert result["url"] == "https://notion.so/page-1"

    def test_page_without_type_in_query_results(self):
        query_result = {
            "results": [
                {
                    "id": "page-1",
                    "properties": {"Status": {"id": "s1", "type": "select", "select": {"id": "opt-1", "name": "Active", "color": "green"}}},
                    "parent": {"type": "database_id", "database_id": "db-1"},
                    "created_by": {"object": "user", "id": "u1"},
                    "last_edited_by": {"object": "user", "id": "u1"},
                    "created_time": "2024-01-01T00:00:00.000Z",
                    "last_edited_time": "2024-01-01T00:00:00.000Z",
                    "archived": False,
                    "in_trash": False,
                    "url": "https://notion.so/page-1",
                }
            ],
            "has_more": False,
        }
        result = _slim_response(query_result)
        page = result["results"][0]
        assert "parent" not in page
        assert "created_by" not in page
        assert "created_time" not in page
        assert "archived" not in page
        assert page["id"] == "page-1"
        assert page["properties"]["Status"]["select"] == {"name": "Active", "color": "green"}


class TestDataSourceMetadata:
    """Data source objects (from get_data_source) have id + properties but no type,
    so the id+(type|properties) heuristic matches them. Their metadata should be stripped
    the same way as pages."""

    def test_data_source_metadata_stripped(self):
        ds = {
            "id": "ds-1",
            "properties": {"Name": {"id": "title", "type": "title", "title": {}}},
            "parent": {"type": "database_id", "database_id": "db-1"},
            "created_by": {"object": "user", "id": "u1"},
            "last_edited_by": {"object": "user", "id": "u1"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
        }
        result = _slim_response(ds)
        assert "parent" not in result
        assert "created_by" not in result
        assert "last_edited_by" not in result
        assert "created_time" not in result
        assert "last_edited_time" not in result
        assert result["id"] == "ds-1"
        assert "properties" in result


class TestRichText:
    def test_default_annotations_stripped_entirely(self):
        item = {
            "type": "text",
            "text": {"content": "Hello", "link": None},
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "Hello",
            "href": None,
        }
        result = _slim_response({"rich_text": [item]})
        rt = result["rich_text"][0]
        assert "annotations" not in rt
        assert "plain_text" not in rt
        assert "href" not in rt
        assert rt["text"] == {"content": "Hello"}
        assert rt["type"] == "text"

    def test_non_default_annotations_keep_only_non_defaults(self):
        item = {
            "type": "text",
            "text": {"content": "Bold text", "link": None},
            "annotations": {
                "bold": True,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
            "plain_text": "Bold text",
            "href": None,
        }
        result = _slim_response({"rich_text": [item]})
        rt = result["rich_text"][0]
        assert rt["annotations"] == {"bold": True}

    def test_multiple_non_default_annotations(self):
        item = {
            "type": "text",
            "text": {"content": "Fancy", "link": None},
            "annotations": {
                "bold": True,
                "italic": True,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "red",
            },
            "plain_text": "Fancy",
            "href": None,
        }
        result = _slim_response({"rich_text": [item]})
        rt = result["rich_text"][0]
        assert rt["annotations"] == {"bold": True, "italic": True, "color": "red"}

    def test_plain_text_removed(self):
        item = {
            "type": "text",
            "text": {"content": "Hello"},
            "plain_text": "Hello",
        }
        result = _slim_response({"rich_text": [item]})
        assert "plain_text" not in result["rich_text"][0]

    def test_text_link_null_stripped(self):
        item = {
            "type": "text",
            "text": {"content": "Hello", "link": None},
        }
        result = _slim_response({"rich_text": [item]})
        assert "link" not in result["rich_text"][0]["text"]

    def test_text_link_present_kept(self):
        item = {
            "type": "text",
            "text": {"content": "Click", "link": {"url": "https://example.com"}},
        }
        result = _slim_response({"rich_text": [item]})
        assert result["rich_text"][0]["text"]["link"] == {"url": "https://example.com"}

    def test_mention_user_plain_text_kept(self):
        """plain_text is the only human-readable content for mention items."""
        item = {
            "type": "mention",
            "mention": {"type": "user", "user": {"id": "user-123"}},
            "plain_text": "@John Doe",
            "href": None,
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
        }
        result = _slim_response({"rich_text": [item]})
        rt = result["rich_text"][0]
        # annotations stripped (all defaults), href stripped (null), plain_text KEPT
        assert "annotations" not in rt
        assert "href" not in rt
        assert rt["plain_text"] == "@John Doe"
        assert rt["type"] == "mention"

    def test_mention_page_plain_text_and_href_kept(self):
        """For page mentions, both plain_text and href are preserved."""
        item = {
            "type": "mention",
            "mention": {"type": "page", "page": {"id": "page-456"}},
            "plain_text": "My Page",
            "href": "https://notion.so/page-456",
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
        }
        result = _slim_response({"rich_text": [item]})
        rt = result["rich_text"][0]
        # annotations stripped (all defaults), plain_text KEPT, href KEPT
        assert "annotations" not in rt
        assert rt["plain_text"] == "My Page"
        assert rt["href"] == "https://notion.so/page-456"

    def test_equation_plain_text_kept(self):
        """For equation items, plain_text is the rendered representation."""
        item = {
            "type": "equation",
            "equation": {"expression": "E = mc^2"},
            "plain_text": "E = mc^2",
            "href": None,
            "annotations": {
                "bold": False,
                "italic": False,
                "strikethrough": False,
                "underline": False,
                "code": False,
                "color": "default",
            },
        }
        result = _slim_response({"rich_text": [item]})
        rt = result["rich_text"][0]
        # annotations stripped (all defaults), href stripped (null), plain_text KEPT
        assert "annotations" not in rt
        assert "href" not in rt
        assert rt["plain_text"] == "E = mc^2"
        assert rt["equation"] == {"expression": "E = mc^2"}

    def test_caption_array_slimmed(self):
        """Caption arrays get the same rich_text slimming treatment."""
        data = {
            "caption": [
                {
                    "type": "text",
                    "text": {"content": "An image", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "An image",
                    "href": None,
                }
            ]
        }
        result = _slim_response(data)
        rt = result["caption"][0]
        assert "annotations" not in rt
        assert "plain_text" not in rt  # type: text, so plain_text stripped
        assert "href" not in rt  # null stripped
        assert "link" not in rt["text"]  # null stripped
        assert rt["text"] == {"content": "An image"}


class TestSelectMultiSelect:
    def test_select_id_stripped(self):
        data = {
            "select": {"id": "opt-1", "name": "Done", "color": "green"},
        }
        result = _slim_response(data)
        assert result["select"] == {"name": "Done", "color": "green"}

    def test_multi_select_id_stripped(self):
        data = {
            "multi_select": [
                {"id": "opt-1", "name": "Tag A", "color": "blue"},
                {"id": "opt-2", "name": "Tag B", "color": "red"},
            ],
        }
        result = _slim_response(data)
        assert result["multi_select"] == [
            {"name": "Tag A", "color": "blue"},
            {"name": "Tag B", "color": "red"},
        ]

    def test_select_name_kept(self):
        data = {"select": {"id": "x", "name": "Active"}}
        result = _slim_response(data)
        assert result["select"]["name"] == "Active"
        assert "id" not in result["select"]

    def test_status_id_stripped(self):
        """Status properties use the same {id, name, color} structure as select."""
        data = {
            "status": {"id": "status-1", "name": "In Progress", "color": "yellow"},
        }
        result = _slim_response(data)
        assert result["status"] == {"name": "In Progress", "color": "yellow"}
        assert "id" not in result["status"]


class TestListResponses:
    def test_type_stripped_from_list_response(self):
        data = {
            "object": "list",
            "type": "block",
            "block": {},
            "results": [],
            "has_more": False,
            "next_cursor": None,
        }
        result = _slim_response(data)
        assert "type" not in result
        assert "object" not in result
        assert "block" not in result
        assert "next_cursor" not in result  # null stripped
        assert result["results"] == []
        assert result["has_more"] is False

    def test_page_or_data_source_empty_stripped(self):
        data = {
            "results": [{"id": "p1", "type": "page"}],
            "has_more": False,
            "page_or_data_source": {},
        }
        result = _slim_response(data)
        assert "page_or_data_source" not in result


class TestBlockContent:
    def test_default_color_stripped(self):
        data = {
            "id": "b1",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [],
                "color": "default",
            },
        }
        result = _slim_response(data)
        assert "color" not in result["paragraph"]

    def test_non_default_color_kept(self):
        data = {
            "id": "b1",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [],
                "color": "red",
            },
        }
        result = _slim_response(data)
        assert result["paragraph"]["color"] == "red"

    def test_is_toggleable_false_stripped(self):
        data = {
            "id": "b1",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [],
                "is_toggleable": False,
                "color": "default",
            },
        }
        result = _slim_response(data)
        assert "is_toggleable" not in result["heading_1"]

    def test_is_toggleable_true_kept(self):
        data = {
            "id": "b1",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [],
                "is_toggleable": True,
            },
        }
        result = _slim_response(data)
        assert result["heading_1"]["is_toggleable"] is True


class TestCommentAndUserObjects:
    def test_comment_object_metadata_stripped(self):
        """Comment objects (id + discussion_id) have metadata stripped."""
        data = {
            "id": "comment-1",
            "discussion_id": "disc-1",
            "parent": {"page_id": "page-abc"},
            "created_by": {"object": "user", "id": "user-1"},
            "created_time": "2024-06-15T10:00:00.000Z",
            "last_edited_time": "2024-06-15T10:00:00.000Z",
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "A comment", "link": None},
                    "annotations": {
                        "bold": False,
                        "italic": False,
                        "strikethrough": False,
                        "underline": False,
                        "code": False,
                        "color": "default",
                    },
                    "plain_text": "A comment",
                    "href": None,
                }
            ],
        }
        result = _slim_response(data)
        # Comment metadata stripped via id+discussion_id heuristic
        assert "parent" not in result
        assert "created_by" not in result
        assert "created_time" not in result
        assert "last_edited_time" not in result
        # Core fields preserved
        assert result["id"] == "comment-1"
        assert result["discussion_id"] == "disc-1"
        # Rich text still gets slimmed
        rt = result["rich_text"][0]
        assert "annotations" not in rt
        assert "plain_text" not in rt  # type: text

    def test_user_object_preserves_type_and_person(self):
        """User objects have type, so id+type heuristic triggers, but name and person are preserved."""
        data = {
            "object": "user",
            "id": "user-1",
            "type": "person",
            "name": "John",
            "person": {"email": "john@example.com"},
        }
        result = _slim_response(data)
        # "object" is always stripped
        assert "object" not in result
        # id+type present so page/block metadata stripping applies, but user doesn't have those keys
        assert result["type"] == "person"
        assert result["name"] == "John"
        assert result["person"] == {"email": "john@example.com"}


class TestEdgeCases:
    def test_empty_dict(self):
        assert _slim_response({}) == {}

    def test_empty_list(self):
        assert _slim_response([]) == []

    def test_primitive_passthrough(self):
        assert _slim_response("hello") == "hello"
        assert _slim_response(42) == 42
        assert _slim_response(True) is True
        assert _slim_response(None) is None

    def test_nested_list_of_dicts(self):
        data = [
            {"object": "block", "id": "b1", "type": "paragraph", "archived": False},
            {"object": "block", "id": "b2", "type": "heading_1", "archived": True},
        ]
        result = _slim_response(data)
        assert len(result) == 2
        assert "object" not in result[0]
        assert "archived" not in result[0]
        assert result[1]["archived"] is True


class TestRealisticRoundTrip:
    """A realistic block response slimmed down to verify end-to-end behavior."""

    def test_paragraph_block_slimmed(self):
        raw = {
            "object": "block",
            "id": "block-abc-123",
            "parent": {"type": "page_id", "page_id": "page-xyz"},
            "created_time": "2024-06-15T10:30:00.000Z",
            "last_edited_time": "2024-06-15T10:35:00.000Z",
            "created_by": {"object": "user", "id": "user-1"},
            "last_edited_by": {"object": "user", "id": "user-1"},
            "has_children": False,
            "archived": False,
            "in_trash": False,
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Hello world", "link": None},
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default",
                        },
                        "plain_text": "Hello world",
                        "href": None,
                    }
                ],
                "color": "default",
            },
        }

        expected = {
            "id": "block-abc-123",
            "has_children": False,
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": "Hello world"},
                    }
                ],
            },
        }

        result = _slim_response(raw)
        assert result == expected

    def test_query_result_with_pages(self):
        """A realistic query response with pages containing properties."""
        raw = {
            "object": "list",
            "type": "page_or_data_source",
            "page_or_data_source": {},
            "request_id": "req-456",
            "results": [
                {
                    "object": "page",
                    "id": "page-1",
                    "type": "page",
                    "created_time": "2024-01-01T00:00:00.000Z",
                    "last_edited_time": "2024-01-02T00:00:00.000Z",
                    "created_by": {"object": "user", "id": "u1"},
                    "last_edited_by": {"object": "user", "id": "u1"},
                    "parent": {"type": "database_id", "database_id": "db-1"},
                    "archived": False,
                    "in_trash": False,
                    "icon": None,
                    "cover": None,
                    "url": "https://notion.so/page-1",
                    "public_url": None,
                    "properties": {
                        "Status": {
                            "id": "prop-1",
                            "type": "select",
                            "select": {"id": "opt-1", "name": "Done", "color": "green"},
                        },
                        "Tags": {
                            "id": "prop-2",
                            "type": "multi_select",
                            "multi_select": [
                                {"id": "opt-a", "name": "Bug", "color": "red"},
                                {"id": "opt-b", "name": "Feature", "color": "blue"},
                            ],
                        },
                        "Name": {
                            "id": "title",
                            "type": "title",
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": "My Page", "link": None},
                                    "annotations": {
                                        "bold": False,
                                        "italic": False,
                                        "strikethrough": False,
                                        "underline": False,
                                        "code": False,
                                        "color": "default",
                                    },
                                    "plain_text": "My Page",
                                    "href": None,
                                }
                            ],
                        },
                    },
                }
            ],
            "next_cursor": None,
            "has_more": False,
        }

        result = _slim_response(raw)

        # Top-level list metadata stripped
        assert "object" not in result
        assert "type" not in result
        assert "page_or_data_source" not in result
        assert "request_id" not in result
        assert "next_cursor" not in result

        page = result["results"][0]
        # Page metadata stripped
        assert "object" not in page
        assert "parent" not in page
        assert "created_by" not in page
        assert "created_time" not in page
        assert "archived" not in page
        assert "icon" not in page  # null stripped
        assert "cover" not in page  # null stripped

        # Select id stripped
        assert page["properties"]["Status"]["select"] == {"name": "Done", "color": "green"}

        # Multi_select ids stripped
        assert page["properties"]["Tags"]["multi_select"] == [
            {"name": "Bug", "color": "red"},
            {"name": "Feature", "color": "blue"},
        ]

        # Rich text in title slimmed
        title_rt = page["properties"]["Name"]["title"][0]
        assert "plain_text" not in title_rt
        assert "annotations" not in title_rt
        assert title_rt["text"] == {"content": "My Page"}


class TestPropertyValueCollision:
    """Verify that property value dicts whose type collides with _PAGE_BLOCK_STRIP_KEYS
    do NOT have their data key stripped (the bug fixed in this commit)."""

    def test_created_time_property_preserved(self):
        prop = {"id": "%3DYVX", "type": "created_time", "created_time": "2024-01-01T00:00:00.000Z"}
        result = _slim_response(prop)
        assert result["created_time"] == "2024-01-01T00:00:00.000Z"
        assert result["type"] == "created_time"

    def test_created_by_property_preserved(self):
        prop = {"id": "nAI%60", "type": "created_by", "created_by": {"object": "user", "id": "user-1"}}
        result = _slim_response(prop)
        assert "created_by" in result
        assert result["created_by"]["id"] == "user-1"

    def test_last_edited_time_property_preserved(self):
        prop = {"id": "abc", "type": "last_edited_time", "last_edited_time": "2024-06-15T10:00:00.000Z"}
        result = _slim_response(prop)
        assert result["last_edited_time"] == "2024-06-15T10:00:00.000Z"

    def test_last_edited_by_property_preserved(self):
        prop = {"id": "def", "type": "last_edited_by", "last_edited_by": {"object": "user", "id": "user-2"}}
        result = _slim_response(prop)
        assert "last_edited_by" in result
        assert result["last_edited_by"]["id"] == "user-2"

    def test_page_metadata_still_stripped(self):
        """Real page objects still get their metadata stripped (regression test)."""
        page = {
            "id": "page-1", "type": "page",
            "parent": {"type": "workspace"},
            "created_by": {"object": "user", "id": "u1"},
            "last_edited_by": {"object": "user", "id": "u1"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
            "properties": {
                "Created": {"id": "ct", "type": "created_time", "created_time": "2024-01-01T00:00:00.000Z"}
            }
        }
        result = _slim_response(page)
        # Page-level metadata stripped
        assert "parent" not in result
        assert "created_by" not in result
        assert "created_time" not in result
        # But property value preserved
        assert result["properties"]["Created"]["created_time"] == "2024-01-01T00:00:00.000Z"

    def test_block_metadata_still_stripped(self):
        """Block objects still get their metadata stripped (regression test)."""
        block = {
            "id": "block-1", "type": "paragraph",
            "parent": {"type": "page_id", "page_id": "page-1"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "created_by": {"object": "user", "id": "u1"},
            "last_edited_by": {"object": "user", "id": "u1"},
            "paragraph": {"rich_text": []}
        }
        result = _slim_response(block)
        assert "parent" not in result
        assert "created_by" not in result
        assert "created_time" not in result
        assert result["type"] == "paragraph"


class TestDatabaseMetadata:
    """Database objects have id + data_sources but no type or properties.
    The extended heuristic should strip metadata from them."""

    def test_database_metadata_stripped(self):
        db = {
            "id": "db-1",
            "title": [{"type": "text", "text": {"content": "My Database"}}],
            "data_sources": [{"id": "ds-1", "type": "default"}],
            "parent": {"type": "workspace", "workspace": True},
            "created_by": {"object": "user", "id": "user-1"},
            "last_edited_by": {"object": "user", "id": "user-1"},
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-02T00:00:00.000Z",
            "archived": False,
            "in_trash": False,
            "is_locked": False,
            "url": "https://notion.so/db-1",
        }
        result = _slim_response(db)
        # Metadata stripped
        assert "parent" not in result
        assert "created_by" not in result
        assert "last_edited_by" not in result
        assert "created_time" not in result
        assert "last_edited_time" not in result
        assert "archived" not in result
        assert "in_trash" not in result
        assert "is_locked" not in result
        # Core fields preserved
        assert result["id"] == "db-1"
        assert "title" in result
        assert "data_sources" in result
        assert result["url"] == "https://notion.so/db-1"

    def test_database_archived_true_preserved(self):
        db = {
            "id": "db-1",
            "data_sources": [{"id": "ds-1"}],
            "archived": True,
        }
        result = _slim_response(db)
        assert result["archived"] is True


class TestCommentMetadata:
    """Comment objects have id + discussion_id but no type or properties.
    The extended heuristic should strip metadata from them."""

    def test_comment_metadata_stripped(self):
        comment = {
            "id": "comment-1",
            "discussion_id": "disc-1",
            "parent": {"page_id": "page-abc"},
            "created_by": {"object": "user", "id": "user-1"},
            "created_time": "2024-06-15T10:00:00.000Z",
            "last_edited_time": "2024-06-15T10:05:00.000Z",
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": "Great work!"},
                }
            ],
        }
        result = _slim_response(comment)
        # Metadata stripped
        assert "parent" not in result
        assert "created_by" not in result
        assert "created_time" not in result
        assert "last_edited_time" not in result
        # Core fields preserved
        assert result["id"] == "comment-1"
        assert result["discussion_id"] == "disc-1"
        assert len(result["rich_text"]) == 1
        assert result["rich_text"][0]["text"] == {"content": "Great work!"}


class TestSelectOptionIdStripping:
    """Property definitions have options arrays with id fields that should be stripped."""

    def test_select_options_id_stripped(self):
        prop_def = {
            "id": "prop-1",
            "type": "select",
            "select": {
                "options": [
                    {"id": "opt-1", "name": "Done", "color": "green"},
                    {"id": "opt-2", "name": "In Progress", "color": "yellow"},
                    {"id": "opt-3", "name": "Not Started", "color": "red"},
                ]
            },
        }
        result = _slim_response(prop_def)
        options = result["select"]["options"]
        assert len(options) == 3
        for opt in options:
            assert "id" not in opt
            assert "name" in opt
            assert "color" in opt
        assert options[0] == {"name": "Done", "color": "green"}
        assert options[1] == {"name": "In Progress", "color": "yellow"}
        assert options[2] == {"name": "Not Started", "color": "red"}

    def test_multi_select_options_id_stripped(self):
        prop_def = {
            "id": "prop-2",
            "type": "multi_select",
            "multi_select": {
                "options": [
                    {"id": "opt-a", "name": "Bug", "color": "red"},
                    {"id": "opt-b", "name": "Feature", "color": "blue"},
                ]
            },
        }
        result = _slim_response(prop_def)
        options = result["multi_select"]["options"]
        assert len(options) == 2
        for opt in options:
            assert "id" not in opt
            assert "name" in opt
            assert "color" in opt
        assert options[0] == {"name": "Bug", "color": "red"}
        assert options[1] == {"name": "Feature", "color": "blue"}
