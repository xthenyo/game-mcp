"""Thread-safe state manager with file locking, atomic writes, and archive."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

from .models import TeamState, Task, TaskStatus

# Lock size large enough to cover any realistic lock file
_LOCK_SIZE = 4096

if sys.platform == "win32":
    import msvcrt

    def _lock(fd):
        fd.seek(0)
        msvcrt.locking(fd.fileno(), msvcrt.LK_LOCK, _LOCK_SIZE)

    def _unlock(fd):
        try:
            fd.seek(0)
            msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, _LOCK_SIZE)
        except OSError:
            pass
else:
    import fcntl

    def _lock(fd):
        fcntl.flock(fd, fcntl.LOCK_EX)

    def _unlock(fd):
        fcntl.flock(fd, fcntl.LOCK_UN)


class StateManager:
    def __init__(self, state_file: Path):
        self._state_file = state_file
        self._lock_file = state_file.with_suffix(".lock")
        self._archive_dir = state_file.parent / "archive"

    @contextmanager
    def lock(self) -> Generator[TeamState, None, None]:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        # Ensure lock file has enough bytes for Windows locking
        if not self._lock_file.exists() or self._lock_file.stat().st_size < _LOCK_SIZE:
            self._lock_file.write_bytes(b"\0" * _LOCK_SIZE)

        with open(self._lock_file, "r+b") as lock_fd:
            _lock(lock_fd)
            try:
                state = self._load()
                yield state
                self._save(state)
            finally:
                _unlock(lock_fd)

    def read(self) -> TeamState:
        return self._load()

    def archive_task(self, task: Task) -> str:
        """Archive a completed task. MUST be called inside lock() context."""
        self._archive_dir.mkdir(parents=True, exist_ok=True)

        month = datetime.now().strftime("%Y-%m")
        archive_file = self._archive_dir / f"done-{month}.json"

        if archive_file.exists():
            archive = json.loads(archive_file.read_text(encoding="utf-8"))
        else:
            archive = {"tasks": []}

        archive["tasks"].append(task.model_dump())

        # Atomic write to prevent corruption
        fd, tmp_path = tempfile.mkstemp(
            dir=self._archive_dir, prefix=".archive-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(archive, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, archive_file)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        return str(archive_file)

    def read_archive(self, month: str | None = None) -> list[dict]:
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        archive_file = self._archive_dir / f"done-{month}.json"
        if archive_file.exists():
            data = json.loads(archive_file.read_text(encoding="utf-8"))
            return data.get("tasks", [])
        return []

    def _load(self) -> TeamState:
        if self._state_file.exists():
            raw = json.loads(self._state_file.read_text(encoding="utf-8"))
            version = raw.get("schema_version", 1)
            if version < 5:
                raw.pop("phase", None)
                raw.pop("activity", None)
                raw.pop("agents", None)
                for task in raw.get("tasks", []):
                    task.setdefault("locked_by", None)
                    task.setdefault("agent_prompt", "")
                    task.setdefault("files", [])
            if version < 6:
                priority_map = {"P0": 10, "P1": 30, "P2": 50, "P3": 70}
                for task in raw.get("tasks", []):
                    old_prio = task.get("priority", "P2")
                    if isinstance(old_prio, str):
                        task["priority"] = priority_map.get(old_prio, 50)
            raw["schema_version"] = 6
            return TeamState.model_validate(raw)
        return TeamState()

    def _save(self, state: TeamState) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=self._state_file.parent,
            prefix=".state-",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(state.model_dump_json(indent=2))
            os.replace(tmp_path, self._state_file)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
