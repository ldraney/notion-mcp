# notion-mcp

MCP (Model Context Protocol) server that wraps [`ldraney/notion-sdk`](https://github.com/ldraney/notion-sdk) — a Python SDK for the Notion API v2025-09-03.

## Overview

This project exposes the full Notion Python SDK as MCP tools, allowing AI assistants (Claude, etc.) to interact with Notion workspaces through a standardized tool interface.

## SDK Coverage

Every method in `notion-sdk` maps to an MCP tool, organized by module:

### Pages
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `create_page` | `create_page()` | `POST /v1/pages` |
| `get_page` | `get_page()` | `GET /v1/pages/{id}` |
| `update_page` | `update_page()` | `PATCH /v1/pages/{id}` |
| `archive_page` | `archive_page()` | `PATCH /v1/pages/{id}` |
| `move_page` | `move_page()` | `POST /v1/pages/{id}/move` |

### Databases
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `create_database` | `create_database()` | `POST /v1/databases` |
| `get_database` | `get_database()` | `GET /v1/databases/{id}` |
| `update_database` | `update_database()` | `PATCH /v1/databases/{id}` |
| `archive_database` | `archive_database()` | `PATCH /v1/databases/{id}` |
| `query_database` | `query_database()` | auto-resolves data source, then `POST /v1/data_sources/{id}/query` |

### Data Sources
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `get_data_source` | `get_data_source()` | `GET /v1/data_sources/{id}` |
| `update_data_source` | `update_data_source()` | `PATCH /v1/data_sources/{id}` |
| `query_data_source` | `query_data_source()` | `POST /v1/data_sources/{id}/query` |
| `list_data_source_templates` | `list_data_source_templates()` | `GET /v1/data_sources/{id}/templates` |

### Blocks
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `get_block` | `get_block()` | `GET /v1/blocks/{id}` |
| `get_block_children` | `get_block_children()` | `GET /v1/blocks/{id}/children` |
| `append_block_children` | `append_block_children()` | `PATCH /v1/blocks/{id}/children` |
| `update_block` | `update_block()` | `PATCH /v1/blocks/{id}` |
| `delete_block` | `delete_block()` | `DELETE /v1/blocks/{id}` |

### Users
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `get_users` | `get_users()` | `GET /v1/users` |
| `get_self` | `get_self()` | `GET /v1/users/me` |

### Comments
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `create_comment` | `create_comment()` | `POST /v1/comments` |
| `get_comments` | `get_comments()` | `GET /v1/comments` |

### Search
| Tool | SDK Method | Notion Endpoint |
|---|---|---|
| `search` | `search()` | `POST /v1/search` |

**21 tools total** covering the complete Notion API v2025-09-03 surface.

## Architecture

```
notion-mcp/
├── src/
│   └── notion_mcp/
│       ├── server.py          # MCP server entry point
│       ├── tools/
│       │   ├── pages.py       # Page tools
│       │   ├── databases.py   # Database & data source tools
│       │   ├── blocks.py      # Block tools
│       │   ├── users.py       # User tools
│       │   ├── comments.py    # Comment tools
│       │   └── search.py      # Search tools
│       └── ...
├── tests/
├── pyproject.toml
└── README.md
```

Each tool module mirrors the SDK's mixin structure, keeping a clean 1:1 mapping.

## Prerequisites

- Python >= 3.10
- A Notion integration API key (`NOTION_API_KEY`)
- [`notion-sdk`](https://github.com/ldraney/notion-sdk) (installed as a dependency)

## Setup

```bash
# Clone
git clone https://github.com/ldraney/notion-mcp.git
cd notion-mcp

# Install
pip install -e .

# Configure
export NOTION_API_KEY="ntn_..."
```

## Usage

### With Claude Code

Add to your Claude Code MCP config (`~/.claude/settings.json` or project settings):

```json
{
  "mcpServers": {
    "notion": {
      "command": "python",
      "args": ["-m", "notion_mcp"],
      "env": {
        "NOTION_API_KEY": "ntn_..."
      }
    }
  }
}
```

### Standalone

```bash
python -m notion_mcp
```

## Related

- [`ldraney/notion-sdk`](https://github.com/ldraney/notion-sdk) — The underlying Python SDK this server wraps
