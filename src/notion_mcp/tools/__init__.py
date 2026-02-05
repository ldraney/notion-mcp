"""Tool registration — imports every tool module so @mcp.tool() decorators fire."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Import all tool modules, which register tools via the module-level functions."""
    from . import pages  # noqa: F401
    from . import databases  # noqa: F401
    from . import blocks  # noqa: F401
    from . import users  # noqa: F401
    from . import comments  # noqa: F401
    from . import search  # noqa: F401
