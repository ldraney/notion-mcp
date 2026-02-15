# Development Guide

## Project Structure

```
src/notion_mcp/
  server.py          # FastMCP server entry point (main())
  tools/
    pages.py         # create, get, update, archive, move
    databases.py     # create, get, update, archive, query + data source tools
    blocks.py        # get, children, append, update, delete
    users.py         # get_users, get_self
    comments.py      # create, get
    search.py        # search
docs/index.html      # GitHub Pages landing site
manifest.json        # .mcpb desktop extension manifest
```

## Setup

```bash
# Install dependencies
uv sync

# Run the server locally
export NOTION_API_KEY="ntn_..."
uv run python -m notion_mcp

# Run tests
uv run pytest
```

## Adding/Modifying Tools

Each tool module in `src/notion_mcp/tools/` maps 1:1 to SDK methods. When adding a tool:

1. Use `@mcp.tool()` decorator
2. Parameters must use `Annotated[type, Field(description=...)]` — FastMCP only puts descriptions in JSON schema from this pattern, NOT from docstrings
3. Accept `str | dict` / `str | list` for structured params — LLMs frequently pass raw objects instead of JSON strings. Use `_parse_json()` helper to normalize.
4. Register the tool module in `server.py`

## Releasing

CI auto-publishes on push to `main` when the version is bumped.

1. Bump version in **both** `pyproject.toml` and `manifest.json` (CI fails if they differ)
2. Push to `main` (via PR or direct if you have admin)
3. CI does the rest: publish to PyPI (OIDC, no token) → build `.mcpb` → create GitHub Release with `.mcpb` attached

If the version is unchanged, CI skips everything (~10s no-op).

Download link (always latest): `https://github.com/ldraney/notion-mcp/releases/latest/download/notion-mcp-ldraney.mcpb`

## Branch Workflow

- **Never develop directly on `main`** — always use feature branches in worktrees
- Worktrees live in `.worktrees/` (gitignored) inside the project
- `.mcp.json` is committed to the repo — it overrides `~/.mcp.json` so agents in worktrees automatically get the correct MCP server config
- Branch protection on `main` requires PRs (use `--admin` to bypass)
- Pattern: implement → review agent → fix findings → merge

### Creating a worktree for a feature branch

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
cd .worktrees/<branch-name>
uv sync
# .mcp.json is already there from the repo — agents get MCP tools automatically
```
