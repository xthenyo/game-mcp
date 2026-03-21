"""Cross-agent context tools — decision log and session context."""

from __future__ import annotations

from typing import Optional

import os
import tempfile
from datetime import datetime, timedelta

from .._context import BIBLE_ROOT, DECISIONS_FILE, mcp
from ..state.manager import now_str
from ..state.models import VALID_ROLES

STALE_THRESHOLD_HOURS = 4


def _ensure_decisions_file() -> None:
    if not DECISIONS_FILE.exists():
        DECISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        DECISIONS_FILE.write_text(
            "# Decision Log\n\n"
            "Decisions made by agents. Every agent reads this on startup.\n"
            "Auto-trimmed to 200 lines.\n\n",
            encoding="utf-8",
        )


def _trim_decisions(max_lines: int = 200) -> None:
    if not DECISIONS_FILE.exists():
        return
    lines = DECISIONS_FILE.read_text(encoding="utf-8").splitlines()
    if len(lines) > max_lines:
        header = lines[:4]
        body = lines[4:]
        trimmed = body[-(max_lines - 4):]
        content = "\n".join(header + trimmed) + "\n"
        # Atomic write to prevent race condition during concurrent trims
        fd, tmp_path = tempfile.mkstemp(
            dir=str(DECISIONS_FILE.parent), prefix=".decisions-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, DECISIONS_FILE)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


VALID_TAGS = frozenset({"ARCH", "ART", "PERF", "BUG", "API", "NAMING", "STYLE", "TOOL", "CONFIG"})


@mcp.tool(description="Log a tagged decision. Tags: ARCH ART PERF BUG API NAMING STYLE TOOL CONFIG.")
def log_decision(role: str, decision: str, tag: str = "", context: str = "") -> dict:
    """Record a decision to workflow/decisions.md."""
    _ensure_decisions_file()

    if len(decision) > 200:
        decision = decision[:197] + "..."
    if len(context) > 100:
        context = context[:97] + "..."

    tag_str = f"[{tag.upper()}] " if tag and tag.upper() in VALID_TAGS else ""
    entry = f"- **[{now_str()}] {role.upper()}:** {tag_str}{decision}"
    if context:
        entry += f" _{context}_"
    entry += "\n"

    with open(DECISIONS_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    _trim_decisions()
    return {"logged": True, "message": f"Decision logged by {role}: {decision[:60]}..."}


@mcp.tool(description="Read recent decisions made by all agents")
def get_decisions(last_n: int = 20) -> dict:
    """Read the most recent decisions from the decision log."""
    _ensure_decisions_file()
    content = DECISIONS_FILE.read_text(encoding="utf-8")
    lines = [l for l in content.splitlines() if l.startswith("- **[")]
    recent = lines[-last_n:] if len(lines) > last_n else lines
    return {"decisions": recent, "count": len(recent), "total": len(lines)}


@mcp.tool(description="Get project state for an agent starting work.")
def get_context(role: str) -> dict:
    """One-call context for an agent starting a new session."""
    from .._context import state_manager

    role = role.upper()
    state = state_manager.read()

    my_tasks_raw = [t for t in state.tasks if t.role == role and t.status.value != "DONE"]
    my_tasks_raw.sort(key=lambda t: t.priority)

    blocked = []
    actionable = []
    for t in my_tasks_raw:
        is_blocked = False
        for dep_id in t.depends_on:
            dep = state.get_task(dep_id)
            if dep and dep.status.value != "DONE":
                blocked.append({"task_id": t.id, "title": t.title, "blocked_by": dep_id})
                is_blocked = True
                break
        if not is_blocked:
            actionable.append(t)

    file_conflicts = []
    my_files = set()
    for t in actionable:
        for f in t.files:
            my_files.add(f.lower().replace("\\", "/"))

    if my_files:
        for t in state.tasks:
            if t.role == role or t.status.value == "DONE":
                continue
            for f in t.files:
                if f.lower().replace("\\", "/") in my_files:
                    file_conflicts.append({
                        "my_file": f, "other_task_id": t.id,
                        "other_role": t.role, "other_task": t.title,
                    })

    others_working = [
        {"role": t.role, "task": t.title, "id": t.id}
        for t in state.tasks if t.role != role and t.status.value == "IN_PROGRESS"
    ]

    _ensure_decisions_file()
    content = DECISIONS_FILE.read_text(encoding="utf-8")
    decision_lines = [l for l in content.splitlines() if l.startswith("- **[")]
    recent_decisions = decision_lines[-5:] if len(decision_lines) > 5 else decision_lines

    result = {}
    if file_conflicts:
        result["file_conflicts"] = file_conflicts
        result["warning"] = "File overlap with other tasks — coordinate before editing"
    if blocked:
        result["blocked_tasks"] = blocked

    result["others_working_on"] = others_working
    result["recent_decisions"] = recent_decisions
    result["role"] = role
    result["total_active_tasks"] = len(state.tasks)
    result["your_actionable_task_count"] = len(actionable)
    result["your_tasks"] = [t.model_dump() for t in actionable]

    open_tasks = [t for t in actionable if t.status.value == "OPEN"]
    if open_tasks:
        next_t = open_tasks[0]
        result["next_task"] = {
            "id": next_t.id,
            "title": next_t.title,
            "priority": next_t.priority,
            "agent_prompt": next_t.agent_prompt,
            "files": next_t.files,
            "instruction": f"claim_task({next_t.id}, '{role}') to start",
        }

    # LEAD gets a full project dashboard — all tasks, all roles, Bible status
    if role == "LEAD":
        all_tasks = state.tasks

        # Tasks by status
        status_counts = {}
        for t in all_tasks:
            s = t.status.value
            status_counts[s] = status_counts.get(s, 0) + 1
        result["project_status"] = status_counts

        # Tasks by role
        role_summary = {}
        for r in sorted(VALID_ROLES - {"LEAD"}):
            role_tasks = [t for t in all_tasks if t.role == r]
            if role_tasks:
                role_summary[r] = {
                    "total": len(role_tasks),
                    "open": sum(1 for t in role_tasks if t.status.value == "OPEN"),
                    "in_progress": sum(1 for t in role_tasks if t.status.value == "IN_PROGRESS"),
                    "blocked": sum(1 for t in role_tasks if t.status.value == "BLOCKED"),
                }
        result["tasks_by_role"] = role_summary

        # All tasks list (compact) for LEAD overview
        result["all_tasks"] = [
            {"id": t.id, "title": t.title, "role": t.role,
             "status": t.status.value, "priority": t.priority,
             "locked_by": t.locked_by, "depends_on": t.depends_on}
            for t in sorted(all_tasks, key=lambda t: t.priority)
        ]

        # Bible completion snapshot
        from .bible import _scan_section, BIBLE_SECTIONS
        bible_summary = {}
        for section_id, section_name in BIBLE_SECTIONS:
            info = _scan_section(BIBLE_ROOT / section_id)
            if info["exists"]:
                bible_summary[section_id] = {
                    "name": section_name,
                    "files": info["files"],
                    "completion": info["completion"],
                }
        if bible_summary:
            result["bible_status"] = bible_summary

        # Stale task detection — flag IN_PROGRESS tasks older than threshold
        stale = []
        now = datetime.now()
        for t in all_tasks:
            if t.status.value != "IN_PROGRESS":
                continue
            # Parse last history entry timestamp
            if t.history:
                last_entry = t.history[-1]
                try:
                    ts_str = last_entry.split("]")[0].lstrip("[").strip()
                    last_ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    if now - last_ts > timedelta(hours=STALE_THRESHOLD_HOURS):
                        stale.append({
                            "task_id": t.id, "title": t.title, "role": t.role,
                            "locked_by": t.locked_by,
                            "stuck_hours": round((now - last_ts).total_seconds() / 3600, 1),
                            "fix": f"update_task({t.id}, 'OPEN', caller_role='LEAD', note='reset stale task')",
                        })
                except (ValueError, IndexError):
                    pass
        if stale:
            result["stale_tasks"] = stale
            result["stale_warning"] = f"{len(stale)} task(s) stuck IN_PROGRESS for >{STALE_THRESHOLD_HOURS}h — consider resetting"

    return result
