"""Core domain models and scheduler skeleton for PawPal+.

This module defines class stubs derived from the UML diagram so scheduling
logic can be implemented incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional


WINDOW_RANGES: Dict[str, tuple[int, int]] = {
    "morning": (6 * 60, 11 * 60),
    "afternoon": (11 * 60, 17 * 60),
    "evening": (17 * 60, 21 * 60),
    "night": (21 * 60, 24 * 60),
    "anytime": (0, 24 * 60),
}


def _parse_window(window: str) -> Optional[tuple[int, int]]:
    """Parse a named or HH:MM-HH:MM window into minute offsets."""
    normalized = window.strip().lower()
    if normalized in WINDOW_RANGES:
        return WINDOW_RANGES[normalized]
    if "-" not in normalized:
        return None
    start_raw, end_raw = [part.strip() for part in normalized.split("-", 1)]
    try:
        start_hour, start_minute = [int(part) for part in start_raw.split(":", 1)]
        end_hour, end_minute = [int(part) for part in end_raw.split(":", 1)]
    except ValueError:
        return None
    start = (start_hour * 60) + start_minute
    end = (end_hour * 60) + end_minute
    if start < 0 or end < 0 or start > 24 * 60 or end > 24 * 60 or start >= end:
        return None
    return start, end


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
    constraints: Dict[str, Any] = field(default_factory=dict)
    pet_id: Optional[str] = None
    status: str = "pending"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.status = "completed"

    def is_due(self, on_date: date) -> bool:
        """Return whether this task is due on the provided date."""
        recurrence = (self.recurrence or "daily").strip().lower()
        if recurrence == "daily":
            return True
        if recurrence in {"once", "one-time", "one_time", "none"}:
            if self.due_by is None:
                return True
            return self.due_by.date() == on_date
        if recurrence == "weekly":
            due_day = self.constraints.get("due_weekday")
            if isinstance(due_day, int) and 0 <= due_day <= 6:
                return on_date.weekday() == due_day
            if self.due_by is not None:
                return on_date.weekday() == self.due_by.weekday()
            return False
        if recurrence == "weekdays":
            return on_date.weekday() < 5
        if recurrence == "weekends":
            return on_date.weekday() >= 5
        return True

    def fits_window(self, window: str) -> bool:
        """Return whether the task can be scheduled in the given time window."""
        if not self.preferred_windows:
            return True
        normalized = window.strip().lower()
        return normalized in {w.strip().lower() for w in self.preferred_windows}

    def score(self, owner: Owner, pet: Pet) -> float:
        """Compute a ranking score for this task based on owner and pet context."""
        score = float(self.priority * 10)

        # Required tasks are strongly preferred by the planner.
        if self.required:
            score += 25.0

        # Urgency bonus increases as due time approaches.
        if self.due_by is not None:
            hours_to_due = (self.due_by - datetime.now()).total_seconds() / 3600
            if hours_to_due <= 0:
                score += 30.0
            elif hours_to_due <= 12:
                score += 20.0
            elif hours_to_due <= 24:
                score += 10.0

        # Reward windows that align with owner preferences.
        if owner.preferred_time_windows and self.preferred_windows:
            owner_windows = {w.strip().lower() for w in owner.preferred_time_windows}
            task_windows = {w.strip().lower() for w in self.preferred_windows}
            if owner_windows.intersection(task_windows):
                score += 5.0

        preferred_categories = owner.get_preference("preferred_categories")
        if isinstance(preferred_categories, list) and self.category in preferred_categories:
            score += 3.0

        category_weights = owner.get_preference("category_weights")
        if isinstance(category_weights, dict):
            weight = category_weights.get(self.category)
            if isinstance(weight, (int, float)):
                score += float(weight)

        # Special-needs pets should prioritize meds/checkups where possible.
        if pet.special_needs and self.category.lower() in {"medication", "medical", "health"}:
            score += 6.0

        # Slight efficiency bonus for short tasks when time is constrained.
        if owner.daily_time_available_min <= 60:
            score += max(0.0, 3.0 - (self.duration_min / 20.0))

        return score


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age_group: str
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize task lookup indices for this pet."""
        # Maintain an index for fast task lookups/removals by ID.
        self._task_index: Dict[str, int] = {
            task.task_id: idx for idx, task in enumerate(self.tasks)
        }

    def add_task(self, task: Task) -> None:
        """Add a new care task to this pet."""
        task.pet_id = self.pet_id
        self.tasks.append(task)
        self._task_index[task.task_id] = len(self.tasks) - 1

    def remove_task(self, task_id: str) -> None:
        """Remove a task by task identifier."""
        task_idx = self._task_index.get(task_id)
        if task_idx is None:
            return
        self.tasks.pop(task_idx)
        self._task_index = {task.task_id: idx for idx, task in enumerate(self.tasks)}

    def get_task(self, task_id: str) -> Optional[Task]:
        """Return a task by ID when present."""
        task_idx = self._task_index.get(task_id)
        if task_idx is None:
            return None
        return self.tasks[task_idx]

    def get_due_tasks(self, for_date: date) -> List[Task]:
        """Return tasks due on the requested date."""
        return [task for task in self.tasks if task.is_due(for_date)]


@dataclass
class Owner:
    owner_id: str
    name: str
    daily_time_available_min: int
    preferences: Dict[str, Any] = field(default_factory=dict)
    preferred_time_windows: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Remove a pet by identifier."""
        self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]

    def set_time_available(self, minutes: int) -> None:
        """Set total minutes available for pet care during the day."""
        self.daily_time_available_min = minutes

    def set_preference(self, key: str, value: Any) -> None:
        """Set or update an owner preference."""
        self.preferences[key] = value

    def get_preference(self, key: str) -> Optional[Any]:
        """Get a preference by key if present."""
        return self.preferences.get(key)


@dataclass
class PlannedItem:
    pet_id: str
    pet_name: str
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
    """Stateless scheduler API for building daily plans."""

    def generate_daily_plan(self, owner: Owner, pet: Pet, plan_date: date) -> DailyPlan:
        """Build a plan for a single pet while keeping owner context."""
        due_tasks = pet.get_due_tasks(plan_date)
        filtered = self.filter_by_constraints(due_tasks, owner)
        ranked = self.rank_tasks(filtered, owner, pet)
        items = self.allocate_time(ranked, owner.daily_time_available_min)
        for item in items:
            item.pet_id = pet.pet_id
            item.pet_name = pet.name
        scheduled_ids = {item.task.task_id for item in items}
        skipped = [task for task in ranked if task.task_id not in scheduled_ids]

        plan = DailyPlan(
            plan_date=plan_date,
            total_available_min=owner.daily_time_available_min,
            total_scheduled_min=sum(item.task.duration_min for item in items),
            items=items,
            skipped_tasks=skipped,
        )
        plan.explanations = self.build_explanations(plan.items, plan.skipped_tasks)
        return plan

    def generate_owner_daily_plan(
        self,
        owner: Owner,
        plan_date: date,
        candidate_tasks: Optional[List[Task]] = None,
    ) -> DailyPlan:
        """Build one daily plan across all pets owned by this owner."""
        owner_pet_by_id = {pet.pet_id: pet for pet in owner.pets}
        owner_pet_name_by_id = {pet.pet_id: pet.name for pet in owner.pets}

        if candidate_tasks is None:
            all_tasks: List[Task] = []
            for pet in owner.pets:
                all_tasks.extend(pet.get_due_tasks(plan_date))
        else:
            all_tasks = [task for task in candidate_tasks if task.is_due(plan_date)]

        filtered = self.filter_by_constraints(all_tasks, owner)

        # Rank globally, but compute score using each task's associated pet context.
        ranked = sorted(
            filtered,
            key=lambda task: task.score(
                owner,
                owner_pet_by_id.get(task.pet_id) or (owner.pets[0] if owner.pets else Pet("unknown", "Unknown", "other", "adult")),
            ),
            reverse=True,
        )

        items = self.allocate_time(ranked, owner.daily_time_available_min)
        for item in items:
            if item.pet_id in owner_pet_name_by_id:
                item.pet_name = owner_pet_name_by_id[item.pet_id]
            elif item.pet_id == "unknown" and item.task.pet_id in owner_pet_name_by_id:
                item.pet_id = item.task.pet_id or "unknown"
                item.pet_name = owner_pet_name_by_id[item.pet_id]
            else:
                item.pet_name = item.pet_name or "Unknown"
        scheduled_ids = {item.task.task_id for item in items}
        skipped = [task for task in ranked if task.task_id not in scheduled_ids]

        plan = DailyPlan(
            plan_date=plan_date,
            total_available_min=owner.daily_time_available_min,
            total_scheduled_min=sum(item.task.duration_min for item in items),
            items=items,
            skipped_tasks=skipped,
        )
        plan.explanations = self.build_explanations(plan.items, plan.skipped_tasks)
        return plan

    def filter_by_constraints(self, tasks: List[Task], owner: Owner) -> List[Task]:
        """Filter out tasks that violate time or preference constraints."""
        owner_windows = {w.strip().lower() for w in owner.preferred_time_windows}
        filtered: List[Task] = []
        max_task_duration = owner.get_preference("max_task_duration")

        for task in tasks:
            if task.constraints.get("enabled") is False:
                continue
            if isinstance(max_task_duration, int) and task.duration_min > max_task_duration and not task.required:
                continue
            if owner_windows and task.preferred_windows and not any(task.fits_window(w) for w in owner_windows):
                if not task.required:
                    continue
            filtered.append(task)

        return filtered

    def rank_tasks(self, tasks: List[Task], owner: Owner, pet: Pet) -> List[Task]:
        """Order tasks by urgency, priority, and fit."""
        return sorted(tasks, key=lambda task: task.score(owner, pet), reverse=True)

    def allocate_time(self, tasks: List[Task], available_min: int) -> List[PlannedItem]:
        """Assign tasks into available time and return planned items."""
        scheduled: List[PlannedItem] = []
        remaining = max(0, available_min)
        cursor = 0

        for task in tasks:
            if task.duration_min <= 0 or task.duration_min > remaining:
                continue

            start = cursor
            if task.preferred_windows:
                ranges = [_parse_window(window) for window in task.preferred_windows]
                valid_ranges = [window_range for window_range in ranges if window_range is not None]
                if valid_ranges:
                    chosen_start, chosen_end = sorted(valid_ranges, key=lambda pair: pair[0])[0]
                    start = max(cursor, chosen_start)
                    if start + task.duration_min > chosen_end:
                        continue

            end = start + task.duration_min
            scheduled.append(
                PlannedItem(
                    pet_id=task.pet_id or "unknown",
                    pet_name="",
                    task=task,
                    start_minute_of_day=start,
                    end_minute_of_day=end,
                    reason_selected=(
                        f"Ranked high (priority={task.priority}, required={task.required}) "
                        f"and fit within remaining time"
                    ),
                )
            )
            cursor = end
            remaining -= task.duration_min

        return scheduled

    def build_explanations(self, items: List[PlannedItem], skipped: List[Task]) -> List[str]:
        """Generate user-facing reasoning for selected and skipped tasks."""
        explanations: List[str] = []
        for item in items:
            start_h = item.start_minute_of_day // 60
            start_m = item.start_minute_of_day % 60
            end_h = item.end_minute_of_day // 60
            end_m = item.end_minute_of_day % 60
            explanations.append(
                f"Scheduled '{item.task.title}' from {start_h:02d}:{start_m:02d} "
                f"to {end_h:02d}:{end_m:02d}: {item.reason_selected}."
            )

        for task in skipped:
            explanations.append(
                f"Skipped '{task.title}' ({task.duration_min} min): insufficient remaining time or window mismatch."
            )

        return explanations
