# notion-mcp

MCP (Model Context Protocol) server that wraps [`ldraney/notion-sdk`](https://github.com/ldraney/notion-sdk) — a Python SDK for the Notion API v2025-09-03.

## Overview

This project exposes the full Notion Python SDK as MCP tools, allowing AI assistants (Claude, etc.) to interact with Notion workspaces through a standardized tool interface.

## Why this over the official Notion MCP servers?

### The problem

There are two official Notion MCP implementations:

1. **Open-source [`makenotion/notion-mcp-server`](https://github.com/makenotion/notion-mcp-server)** (TypeScript) — issues and PRs "not actively monitored," may be sunset in the future
2. **Closed-source hosted MCP at `mcp.notion.com`** — what Claude Desktop's "Connections > Notion" uses

Neither works reliably. This is well-documented in issues like [#142](https://github.com/makenotion/notion-mcp-server/issues/142) ("Two Notion MCP servers, neither work well"). The open-source server was abandoned for 3.5 months after the v2025-09-03 breaking API change, shipped a broken v2.0.0 (Dec 2025), and still has open showstopper bugs in v2.1.0.

### Comparison

| | Official open-source | Official hosted | `ldraney-notion-mcp` |
|---|---|---|---|
| Status | "Not actively monitored" | Closed-source | Actively maintained |
| Language | TypeScript | N/A | Python |
| API version | 2025-09-03 (broken) | Unknown | 2025-09-03 (working) |
| Auth | Bearer token (version header trap) | OAuth only | Bearer token (correct headers always) |
| Serialization | Double-stringifies nested objects ([#196](https://github.com/makenotion/notion-mcp-server/issues/196)) | N/A | Accepts both JSON strings and raw objects |
| Property updates | Blocked by `additionalProperties: false` ([#184](https://github.com/makenotion/notion-mcp-server/issues/184)) | Unknown | Works correctly |
| Database queries | `retrieve-a-database` was missing for 5 weeks | Some tools gated to Enterprise | `query_database` auto-resolves data sources |
| Tool count | 22 | ~10 | 26 |
| Context cost | ~8k+ tokens (est.) | ~21k tokens (measured) | ~8.6k tokens (measured) |
| Convenience tools | None | Limited | `archive_page`, `archive_database`, `query_database` |
| Install | npm | Claude Desktop only | PyPI (`uvx`), `.mcpb` (planned) |

### Key advantages

- **2.5x more token-efficient** — 26 tools in ~8.6k tokens vs the official Claude-managed Notion integration's 12 tools in ~21.4k tokens. Less context overhead means more room for actual conversation
- **Correct API headers always** — Built on [`ldraney-notion-sdk`](https://github.com/ldraney/notion-sdk), which always sends the `Notion-Version: 2025-09-03` header correctly
- **LLM-friendly parameter handling** — `str | dict` union types so tools don't break when LLMs pass raw objects instead of JSON strings
- **Convenience tools** — Operations like `archive_page`, `archive_database`, and `query_database` (with auto data-source resolution) reduce multi-step workflows to single calls
- **Works everywhere** — `uvx`, `pip`, Claude Code, any MCP-compatible client

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

**26 tools total** covering the complete Notion API v2025-09-03 surface.

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
# Clone and install
git clone https://github.com/ldraney/notion-mcp.git
cd notion-mcp
uv sync

# Set your API key
export NOTION_API_KEY="ntn_..."
```

## Usage

### With Claude Code

The repo ships with a `.mcp.json` that configures everything automatically. Just `cd` into the project and start Claude Code — it picks up the config and reads `NOTION_API_KEY` from your environment via `${NOTION_API_KEY}` interpolation.

To use notion-mcp from **other projects**, add this to that project's `.mcp.json`:

```json
{
  "mcpServers": {
    "notion": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/notion-mcp", "python", "-m", "notion_mcp"],
      "env": {
        "NOTION_API_KEY": "${NOTION_API_KEY}"
      }
    }
  }
}
```

Or add it to `~/.mcp.json` to make it available globally across all projects.

See [hello-mcp](https://github.com/ldraney/hello-mcp) for more on the `${VAR}` env secret pattern.

### Standalone

```bash
python -m notion_mcp
```

## Related

- [`ldraney/notion-sdk`](https://github.com/ldraney/notion-sdk) — The underlying Python SDK this server wraps
