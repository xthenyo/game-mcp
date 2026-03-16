"""Structured audit logging with JSONL format and monthly rotation."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class AuditLogger:
    def __init__(self, audit_dir: Path):
        self._audit_dir = audit_dir

    def log(
        self,
        action: str,
        agent: str = "SYSTEM",
        details: dict | None = None,
        phase: str | None = None,
    ) -> None:
        self._audit_dir.mkdir(parents=True, exist_ok=True)

        now = datetime.now()
        filename = f"audit-{now.strftime('%Y-%m')}.jsonl"
        filepath = self._audit_dir / filename

        entry = {
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "agent": agent,
            "action": action,
            "phase": phase,
        }
        if details:
            entry["details"] = details

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
