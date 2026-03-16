"""Doomed Team MCP Server — multi-agent task management for game development."""

from __future__ import annotations

import sys

# ====== FORCE UTF-8 ON WINDOWS ======
# Windows may default to cp1252 for stdio, MCP protocol needs UTF-8.
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from ._context import mcp  # noqa: F401
from ._context import state_manager  # noqa: F401

# Register tool modules
from .tools import bible  # noqa: F401  — Bible doc status + gap detection
from .tools import context  # noqa: F401  — decision log + cross-agent context
from .tools import coordination  # noqa: F401  — task dependencies
from .tools import external  # noqa: F401  — Gemini CLI + Aseprite CLI wrappers
from .tools import tasks  # noqa: F401  — task CRUD with claiming + archive


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
