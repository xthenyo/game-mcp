"""Game MCP Team Server — multi-agent task management for game development."""

from __future__ import annotations

import sys

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from ._context import mcp  # noqa: F401
from ._context import state_manager  # noqa: F401

# Register tool modules
from .tools import bible  # noqa: F401
from .tools import context  # noqa: F401
from .tools import coordination  # noqa: F401
from .tools import external  # noqa: F401
from .tools import tasks  # noqa: F401


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
