"""Task management tools with duplicate detection, claiming, and auto-archive."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Optional

from .._context import mcp, state_manager
from ..state.manager import now_str
from ..state.models import EXECUTOR_ROLES, VALID_ROLES, Task, TaskStatus


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _find_duplicate(title: str, role: str, tasks: list[Task]) -> Optional[Task]:
    for task in tasks:
        if task.status == TaskStatus.DONE:
            continue
        if task.role == role and _similarity(task.title, title) > 0.7:
            return task
    return None


def _find_file_conflicts(files: list[str], tasks: list[Task], exclude_role: str = "") -> list[dict]:
    conflicts = []
    if not files:
        return conflicts
    file_set = {f.lower().replace("\\", "/") for f in files}
    for task in tasks:
        if task.status == TaskStatus.DONE:
            continue
        if exclude_role and task.role == exclude_role:
            continue
        for tf in task.files:
            if tf.lower().replace("\\", "/") in file_set:
                conflicts.append({
                    "task_id": task.id,
                    "title": task.title,
                    "role": task.role,
                    "conflicting_file": tf,
                })
                break
    return conflicts


@mcp.tool(description="Create a new task. Checks for duplicates and file conflicts. Only LEAD should create tasks.")
def create_task(
    title: str,
    role: str,
    priority: int = 50,
    description: str = "",
    agent_prompt: str = "",
    files: Optional[list[str]] = None,
) -> dict:
    """Create a task with duplicate and file conflict detection."""
    role = role.upper()
    if role not in EXECUTOR_ROLES:
        return {"error": f"Tasks can only be assigned to executor roles: {', '.join(sorted(EXECUTOR_ROLES))}. Got '{role}'."}

    if not (0 <= priority <= 100):
        return {"error": f"Priority must be 0-100, got {priority}"}

    task_files = files or []

    with state_manager.lock() as state:
        dup = _find_duplicate(title, role, state.tasks)
        if dup:
            return {
                "error": "DUPLICATE",
                "existing_task": {"id": dup.id, "title": dup.title, "status": dup.status.value, "role": dup.role},
                "message": f"Similar task already exists: #{dup.id} '{dup.title}' ({dup.status.value})",
            }

        file_conflicts = _find_file_conflicts(task_files, state.tasks)

        task_id = state.next_task_id()
        task = Task(
            id=task_id, title=title, role=role, priority=priority,
            status=TaskStatus.OPEN, description=description,
            agent_prompt=agent_prompt, files=task_files,
            created=now_str(), history=[f"{now_str()}: Created by LEAD"],
        )
        state.tasks.append(task)

    result = {"task_id": task_id, "message": f"Task #{task_id} created: {title} -> {role}"}
    if file_conflicts:
        result["file_conflicts"] = file_conflicts
        result["warning"] = "Some files overlap with other active tasks"
    return result


@mcp.tool(description="Claim a task — locks it to your role. LEAD cannot claim tasks.")
def claim_task(task_id: int, role: str) -> dict:
    """Claim a task for your role. Moves to IN_PROGRESS and locks it."""
    role = role.upper()
    if role not in EXECUTOR_ROLES:
        return {"error": f"REJECTED: '{role}' cannot claim tasks. Only: {', '.join(sorted(EXECUTOR_ROLES))}"}

    with state_manager.lock() as state:
        task = state.get_task(task_id)
        if not task:
            return {"success": False, "message": f"Task #{task_id} not found"}
        if task.role != role:
            return {"success": False, "message": f"Task #{task_id} is assigned to {task.role}, not {role}."}
        if task.locked_by and task.locked_by != role:
            return {"success": False, "message": f"Task #{task_id} is already locked by {task.locked_by}."}
        if task.status == TaskStatus.DONE:
            return {"success": False, "message": f"Task #{task_id} is already DONE."}
        if task.status == TaskStatus.IN_PROGRESS and task.locked_by == role:
            return {"success": True, "message": f"Task #{task_id} already claimed by {role}.", "task": task.model_dump()}

        if task.depends_on:
            for dep_id in task.depends_on:
                dep = state.get_task(dep_id)
                if dep and dep.status != TaskStatus.DONE:
                    return {"success": False, "message": f"Blocked: depends on Task #{dep_id} ({dep.title}) — {dep.status.value}"}

        task.status = TaskStatus.IN_PROGRESS
        task.locked_by = role
        task.history.append(f"{now_str()}: Claimed by {role}")

    return {"success": True, "message": f"Task #{task_id} claimed by {role}.", "task": task.model_dump()}


@mcp.tool(description="Complete a task. Requires self_review. LEAD cannot complete.")
def complete_task(task_id: int, role: str, self_review: str, note: str = "") -> dict:
    """Mark task as DONE. Archives to workflow/archive/done-YYYY-MM.json."""
    role = role.upper()
    if role not in EXECUTOR_ROLES:
        return {"error": f"REJECTED: '{role}' cannot complete tasks."}

    if not self_review or len(self_review.strip()) < 20:
        return {"error": "REJECTED: self_review required (min 20 chars)."}

    with state_manager.lock() as state:
        task = state.get_task(task_id)
        if not task:
            return {"success": False, "message": f"Task #{task_id} not found"}
        if task.locked_by and task.locked_by != role:
            return {"success": False, "message": f"Task #{task_id} is locked by {task.locked_by}, not {role}."}
        if task.role != role:
            return {"success": False, "message": f"Task #{task_id} belongs to {task.role}, not {role}."}

        review_short = self_review[:200] + "..." if len(self_review) > 200 else self_review
        entry = f"{now_str()}: DONE by {role} | Review: {review_short}"
        if note:
            entry += f" | Note: {note}"
        task.history.append(entry)
        task.status = TaskStatus.DONE
        archive_path = state_manager.archive_task(task)
        state.tasks = [t for t in state.tasks if t.id != task_id]

    return {"success": True, "message": f"Task #{task_id} completed and archived.", "archived_to": archive_path}


@mcp.tool(description="Get active tasks, optionally filtered by role or status")
def get_tasks(role: Optional[str] = None, status: Optional[str] = None) -> dict:
    """Retrieve active tasks."""
    state = state_manager.read()
    tasks = state.tasks
    if role:
        tasks = [t for t in tasks if t.role == role.upper()]
    if status:
        tasks = [t for t in tasks if t.status == status.upper()]
    return {"tasks": [t.model_dump() for t in tasks], "count": len(tasks)}


@mcp.tool(description="Search tasks by title or description text")
def search_tasks(query: str) -> dict:
    """Full-text search across active task titles and descriptions."""
    state = state_manager.read()
    q = query.lower()
    matches = [t for t in state.tasks if q in t.title.lower() or q in t.description.lower()]
    return {"tasks": [t.model_dump() for t in matches], "count": len(matches)}


@mcp.tool(description="Update task status (BLOCKED or re-opening). Use claim_task/complete_task for normal flow.")
def update_task(task_id: int, status: str, note: Optional[str] = None) -> dict:
    """Change a task's status."""
    try:
        new_status = TaskStatus(status.upper())
    except ValueError:
        return {"success": False, "message": f"Invalid status '{status}'."}

    if new_status == TaskStatus.DONE:
        return {"success": False, "message": "Use complete_task() to mark tasks as DONE."}

    with state_manager.lock() as state:
        task = state.get_task(task_id)
        if not task:
            return {"success": False, "message": f"Task #{task_id} not found"}
        old_status = task.status
        task.status = new_status
        entry = f"{now_str()}: {old_status.value} -> {new_status.value}"
        if note:
            entry += f" ({note})"
        task.history.append(entry)

    return {"success": True, "message": f"Task #{task_id}: {old_status.value} -> {new_status.value}"}


@mcp.tool(description="View archived (completed) tasks for a given month")
def get_archive(month: Optional[str] = None) -> dict:
    """Read completed tasks from archive."""
    tasks = state_manager.read_archive(month)
    return {"tasks": tasks, "count": len(tasks)}
