"""Cross-agent context tools — decision log and session context."""

from __future__ import annotations

from typing import Optional

from .._context import DECISIONS_FILE, mcp
from ..state.manager import now_str


def _ensure_decisions_file() -> None:
    if not DECISIONS_FILE.exists():
        DECISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        DECISIONS_FILE.write_text(
            "# Decision Log\n\n"
            "Decisions made by agents. Every agent reads this on startup.\n"
            "Auto-trimmed to 80 lines.\n\n",
            encoding="utf-8",
        )


def _trim_decisions(max_lines: int = 80) -> None:
    if not DECISIONS_FILE.exists():
        return
    lines = DECISIONS_FILE.read_text(encoding="utf-8").splitlines()
    if len(lines) > max_lines:
        header = lines[:4]
        body = lines[4:]
        trimmed = body[-(max_lines - 4):]
        DECISIONS_FILE.write_text("\n".join(header + trimmed) + "\n", encoding="utf-8")


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
        result["next_task"] = {
            "id": open_tasks[0].id,
            "title": open_tasks[0].title,
            "priority": open_tasks[0].priority,
            "instruction": f"claim_task({open_tasks[0].id}, '{role}') to start",
        }

    return result
