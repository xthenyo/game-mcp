"""Task dependency and coordination tools."""

from __future__ import annotations

from .._context import mcp, state_manager
from ..state.models import TaskStatus


def _has_circular_dep(state, start_id: int, target_id: int, visited: set | None = None) -> bool:
    """Check if adding target_id as dependency of start_id would create a cycle."""
    if visited is None:
        visited = set()
    if target_id in visited:
        return False
    visited.add(target_id)
    target = state.get_task(target_id)
    if not target:
        return False
    for dep_id in target.depends_on:
        if dep_id == start_id:
            return True
        if _has_circular_dep(state, start_id, dep_id, visited):
            return True
    return False


@mcp.tool(description="Add a dependency between tasks (task depends on dependency)")
def add_task_dependency(task_id: int, depends_on_id: int) -> dict:
    """Link task_id as depending on depends_on_id."""
    if task_id == depends_on_id:
        return {"success": False, "message": "A task cannot depend on itself"}

    with state_manager.lock() as state:
        task = state.get_task(task_id)
        dep = state.get_task(depends_on_id)
        if not task:
            return {"success": False, "message": f"Task #{task_id} not found"}
        if not dep:
            return {"success": False, "message": f"Dependency task #{depends_on_id} not found"}
        if depends_on_id in task.depends_on:
            return {"success": False, "message": "Dependency already exists"}
        if _has_circular_dep(state, task_id, depends_on_id):
            return {"success": False, "message": f"REJECTED: circular dependency detected — Task #{depends_on_id} already depends on #{task_id} (directly or transitively)"}
        task.depends_on.append(depends_on_id)

    return {"success": True, "message": f"Task #{task_id} now depends on Task #{depends_on_id}"}


@mcp.tool(description="List tasks that are blocked by unfinished dependencies")
def get_blocked_tasks() -> dict:
    """Find all tasks that have unfinished dependencies."""
    state = state_manager.read()
    blocked = []
    for task in state.tasks:
        if task.status == TaskStatus.DONE:
            continue
        for dep_id in task.depends_on:
            dep = state.get_task(dep_id)
            if dep and dep.status != TaskStatus.DONE:
                blocked.append({
                    "task_id": task.id, "title": task.title,
                    "blocked_by": dep_id, "blocked_by_title": dep.title,
                    "blocked_by_status": dep.status.value,
                })
                break
    return {"blocked_tasks": blocked, "count": len(blocked)}
