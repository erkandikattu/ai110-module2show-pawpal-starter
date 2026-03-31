"""Core domain models and scheduler skeleton for PawPal+.

This module defines class stubs derived from the UML diagram so scheduling
logic can be implemented incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional


@dataclass
class Task:
    task_id: str
    title: str
    category: str
    duration_min: int
    priority: int
    recurrence: str = "daily"
    required: bool = False
    preferred_windows: List[str] = field(default_factory=list)
    due_by: Optional[datetime] = None
    constraints: Dict[str, str] = field(default_factory=dict)

    def is_due(self, on_date: date) -> bool:
        """Return whether this task is due on the provided date."""
        raise NotImplementedError

    def fits_window(self, window: str) -> bool:
        """Return whether the task can be scheduled in the given time window."""
        raise NotImplementedError

    def score(self, owner: Owner, pet: Pet) -> float:
        """Compute a ranking score for this task based on owner and pet context."""
        raise NotImplementedError


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age_group: str
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a new care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task by task identifier."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_due_tasks(self, for_date: date) -> List[Task]:
        """Return tasks due on the requested date."""
        raise NotImplementedError


@dataclass
class Owner:
    owner_id: str
    name: str
    daily_time_available_min: int
    preferences: Dict[str, str] = field(default_factory=dict)
    preferred_time_windows: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def set_time_available(self, minutes: int) -> None:
        """Set total minutes available for pet care during the day."""
        self.daily_time_available_min = minutes

    def set_preference(self, key: str, value: str) -> None:
        """Set or update an owner preference."""
        self.preferences[key] = value

    def get_preference(self, key: str) -> Optional[str]:
        """Get a preference by key if present."""
        return self.preferences.get(key)


@dataclass
class PlannedItem:
    task: Task
    start_minute_of_day: int
    end_minute_of_day: int
    reason_selected: str


@dataclass
class DailyPlan:
    plan_date: date
    total_available_min: int
    total_scheduled_min: int = 0
    items: List[PlannedItem] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    explanations: List[str] = field(default_factory=list)

    def summary(self) -> str:
        """Return a short, human-readable daily plan summary."""
        return (
            f"{self.plan_date.isoformat()}: "
            f"{len(self.items)} tasks scheduled, "
            f"{self.total_scheduled_min}/{self.total_available_min} min used"
        )


class Scheduler:
    def __init__(self, candidate_tasks: Optional[List[Task]] = None) -> None:
        self.candidate_tasks: List[Task] = candidate_tasks or []

    def generate_daily_plan(self, owner: Owner, pet: Pet, plan_date: date) -> DailyPlan:
        """Build a complete plan for one pet on a specific date."""
        raise NotImplementedError

    def filter_by_constraints(self, tasks: List[Task], owner: Owner) -> List[Task]:
        """Filter out tasks that violate time or preference constraints."""
        raise NotImplementedError

    def rank_tasks(self, tasks: List[Task], owner: Owner, pet: Pet) -> List[Task]:
        """Order tasks by urgency, priority, and fit."""
        raise NotImplementedError

    def allocate_time(self, tasks: List[Task], available_min: int) -> List[PlannedItem]:
        """Assign tasks into available time and return planned items."""
        raise NotImplementedError

    def build_explanations(self, items: List[PlannedItem], skipped: List[Task]) -> List[str]:
        """Generate user-facing reasoning for selected and skipped tasks."""
        raise NotImplementedError
