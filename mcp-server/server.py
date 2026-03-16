#!/usr/bin/env python3
"""Backward compatibility shim. Use 'python3 -m doomed.mcp_team.server' instead."""

import sys
from pathlib import Path

# Add src/ to path so doomed package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from doomed.mcp_team.server import main

if __name__ == "__main__":
    main()
