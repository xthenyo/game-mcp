"""Shared context: MCP server instance and core services.

Tool modules import from here, server.py imports tools after setup.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from doomed._project import discover_project_root

from .state.manager import StateManager

PROJECT_ROOT = discover_project_root(anchor=Path(__file__))

STATE_FILE = PROJECT_ROOT / "workflow" / "team-state.json"
BIBLE_ROOT = PROJECT_ROOT / "docs" / "bible"
DECISIONS_FILE = PROJECT_ROOT / "workflow" / "decisions.md"

# FastMCP server instance
mcp = FastMCP("doomed-team")

# State manager — thread-safe JSON persistence for tasks and phases
state_manager = StateManager(STATE_FILE)
