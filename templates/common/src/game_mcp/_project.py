"""Project root discovery for game-mcp modules."""

from __future__ import annotations

import os
from pathlib import Path

_ROOT_MARKERS = ("pyproject.toml", "workflow", "docs", ".claude", "game-mcp.json")


def discover_project_root(anchor: Path | None = None) -> Path:
    """Discover project root via env var, CWD walking, or anchor fallback.

    Resolution order:
    1. GAME_MCP_PROJECT_ROOT environment variable (explicit override)
    2. Walk up from CWD looking for marker files/dirs
    3. Walk up from anchor path (e.g. __file__ of the caller)
    4. Fall back to CWD
    """
    env_root = os.environ.get("GAME_MCP_PROJECT_ROOT")
    if env_root:
        root = Path(env_root).resolve()
        if root.is_dir():
            return root

    cwd = Path.cwd().resolve()
    candidate = cwd
    while candidate != candidate.parent:
        if any((candidate / m).exists() for m in _ROOT_MARKERS):
            return candidate
        candidate = candidate.parent

    if anchor:
        candidate = anchor.resolve()
        while candidate != candidate.parent:
            if any((candidate / m).exists() for m in _ROOT_MARKERS):
                return candidate
            candidate = candidate.parent

    return cwd
