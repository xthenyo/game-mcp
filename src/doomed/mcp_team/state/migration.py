"""Migrate old team-state.json (v1) to new schema (v2)."""

from __future__ import annotations


def migrate_v1_to_v2(raw: dict) -> dict:
    """Migrate v1 state (unversioned) to v2 schema.

    Changes:
    - Adds schema_version: 2
    - Adds sequence_counter (set to max existing task id)
    - Adds depends_on and blocked_by fields to tasks
    - Converts agents from {role: {status, last_seen}} to include new fields
    """
    tasks = raw.get("tasks", [])

    # Determine sequence counter from existing task IDs
    max_id = 0
    for task in tasks:
        task_id = task.get("id", 0)
        if task_id > max_id:
            max_id = task_id
        # Add new fields
        if "depends_on" not in task:
            task["depends_on"] = []
        if "blocked_by" not in task:
            task["blocked_by"] = None

    # Add new agent fields
    agents = raw.get("agents", {})
    for role, agent_data in agents.items():
        if isinstance(agent_data, dict):
            if "current_task" not in agent_data:
                agent_data["current_task"] = None
            if "working_on" not in agent_data:
                agent_data["working_on"] = None

    return {
        "schema_version": 2,
        "phase": raw.get("phase", "DISCOVERY"),
        "sequence_counter": max_id,
        "tasks": tasks,
        "activity": raw.get("activity", []),
        "agents": agents,
    }
