"""Pydantic models for team state management."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    BLOCKED = "BLOCKED"


VALID_ROLES = frozenset({"LEAD", "ENGINEER", "DESIGNER", "ARTIST", "QA"})
EXECUTOR_ROLES = frozenset({"ENGINEER", "DESIGNER", "ARTIST", "QA"})


class Task(BaseModel):
    id: int
    title: str
    role: str
    priority: int = Field(default=50, ge=0, le=100)
    status: TaskStatus = TaskStatus.OPEN
    description: str = ""
    agent_prompt: str = ""
    locked_by: Optional[str] = None
    files: list[str] = Field(default_factory=list)
    created: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    history: list[str] = Field(default_factory=list)
    depends_on: list[int] = Field(default_factory=list)


class TeamState(BaseModel):
    schema_version: int = 6
    sequence_counter: int = 0
    tasks: list[Task] = Field(default_factory=list)

    def next_task_id(self) -> int:
        self.sequence_counter += 1
        return self.sequence_counter

    def get_task(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def tasks_by_role(self, role: str) -> list[Task]:
        return [t for t in self.tasks if t.role == role]

    def active_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status != TaskStatus.DONE]
