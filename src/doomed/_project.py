"""Shared project root discovery for all doomed modules.

Used by mcp_team, mcp_visual, and CLI to find the project root
regardless of how/where the package is installed or invoked.
"""

from __future__ import annotations

import os
from pathlib import Path

_ROOT_MARKERS = ("pyproject.toml", "workflow", "docs", ".claude")


def discover_project_root(anchor: Path | None = None) -> Path:
    """Discover project root via env var, CWD walking, or anchor fallback.

    Resolution order:
    1. DOOMED_PROJECT_ROOT environment variable (explicit override)
    2. Walk up from CWD looking for marker files/dirs
    3. Walk up from anchor path (e.g. __file__ of the caller)
    4. Fall back to CWD
    """
    # 1. Env var override
    env_root = os.environ.get("DOOMED_PROJECT_ROOT")
    if env_root:
        root = Path(env_root).resolve()
        if root.is_dir():
            return root

    # 2. Walk up from CWD
    cwd = Path.cwd().resolve()
    candidate = cwd
    while candidate != candidate.parent:
        if any((candidate / m).exists() for m in _ROOT_MARKERS):
            return candidate
        candidate = candidate.parent

    # 3. Walk up from anchor path (installed package fallback)
    if anchor:
        candidate = anchor.resolve()
        while candidate != candidate.parent:
            if any((candidate / m).exists() for m in _ROOT_MARKERS):
                return candidate
            candidate = candidate.parent

    # Last resort: CWD
    return cwd
