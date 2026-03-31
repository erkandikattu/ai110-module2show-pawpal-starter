"""Unit tests for core PawPal behaviors."""

from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, PlannedItem, Scheduler, Task


def test_mark_complete_updates_task_status() -> None:
    """Calling mark_complete should update task completion status."""
    task = Task(
        task_id="task-1",
        title="Morning walk",
        category="exercise",
        duration_min=30,
        priority=3,
    )

    task.mark_complete()

    assert task.status == "completed"


def test_mark_complete_daily_spawns_next_occurrence() -> None:
    """Completing a daily task should create the next day's pending task."""
    due = datetime(2026, 3, 31, 9, 0)
    pet = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")
    task = Task(
        task_id="task-daily",
        title="Morning walk",
        category="exercise",
        duration_min=30,
        priority=3,
        recurrence="daily",
        due_by=due,
    )
    pet.add_task(task)

    next_task = task.mark_complete(pet=pet)

    assert task.status == "completed"
    assert next_task is not None
    assert next_task.status == "pending"
    assert next_task.due_by == due + timedelta(days=1)
    assert next_task in pet.tasks


def test_mark_complete_weekly_spawns_next_occurrence() -> None:
    """Completing a weekly task should create the next week's pending task."""
    due = datetime(2026, 3, 31, 18, 0)
    pet = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")
    task = Task(
        task_id="task-weekly",
        title="Nail trim",
        category="hygiene",
        duration_min=20,
        priority=2,
        recurrence="weekly",
        due_by=due,
    )
    pet.add_task(task)

    next_task = task.mark_complete(pet=pet)

    assert task.status == "completed"
    assert next_task is not None
    assert next_task.status == "pending"
    assert next_task.due_by == due + timedelta(days=7)
    assert next_task in pet.tasks


def test_add_task_increases_pet_task_count() -> None:
    """Adding a task to a pet should increase its task count by one."""
    pet = Pet(
        pet_id="pet-1",
        name="Milo",
        species="dog",
        age_group="adult",
    )
    initial_count = len(pet.tasks)

    pet.add_task(
        Task(
            task_id="task-2",
            title="Feed dinner",
            category="feeding",
            duration_min=15,
            priority=4,
        )
    )

    assert len(pet.tasks) == initial_count + 1


def test_sort_tasks_by_time_prioritizes_earliest_due() -> None:
    """Tasks with earlier due_by times should come first."""
    scheduler = Scheduler()
    now = datetime.now()
    tasks = [
        Task(
            task_id="t-late",
            title="Late due",
            category="feeding",
            duration_min=15,
            priority=5,
            due_by=now + timedelta(hours=5),
        ),
        Task(
            task_id="t-early",
            title="Early due",
            category="medical",
            duration_min=15,
            priority=1,
            due_by=now + timedelta(hours=1),
        ),
    ]

    sorted_tasks = scheduler.sort_tasks_by_time(tasks)

    assert [task.task_id for task in sorted_tasks] == ["t-early", "t-late"]


def test_sort_tasks_by_time_places_undated_tasks_last() -> None:
    """Tasks without due_by should be sorted after tasks with due_by."""
    scheduler = Scheduler()
    now = datetime.now()
    tasks = [
        Task(
            task_id="t-no-due",
            title="No due",
            category="hygiene",
            duration_min=10,
            priority=5,
        ),
        Task(
            task_id="t-due",
            title="Has due",
            category="feeding",
            duration_min=10,
            priority=1,
            due_by=now + timedelta(hours=2),
        ),
    ]

    sorted_tasks = scheduler.sort_tasks_by_time(tasks)

    assert [task.task_id for task in sorted_tasks] == ["t-due", "t-no-due"]


def test_generate_owner_daily_plan_uses_due_time_ordering() -> None:
    """Owner plan should schedule earliest due tasks first when time is limited."""
    now = datetime.now()
    owner = Owner(owner_id="owner-1", name="Alex", daily_time_available_min=30)
    pet = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")

    pet.add_task(
        Task(
            task_id="t-late-high-priority",
            title="Later task",
            category="exercise",
            duration_min=30,
            priority=5,
            due_by=now + timedelta(hours=6),
        )
    )
    pet.add_task(
        Task(
            task_id="t-early-low-priority",
            title="Earlier task",
            category="medical",
            duration_min=30,
            priority=1,
            due_by=now + timedelta(hours=1),
        )
    )
    owner.add_pet(pet)

    plan = Scheduler().generate_owner_daily_plan(owner, date.today())

    assert [item.task.task_id for item in plan.items] == ["t-early-low-priority"]


def test_filter_tasks_by_completion_status() -> None:
    """Scheduler should filter tasks by completion status."""
    scheduler = Scheduler()
    tasks = [
        Task(
            task_id="t-pending",
            title="Pending task",
            category="feeding",
            duration_min=10,
            priority=2,
            status="pending",
        ),
        Task(
            task_id="t-completed",
            title="Completed task",
            category="exercise",
            duration_min=15,
            priority=3,
            status="completed",
        ),
    ]

    filtered = scheduler.filter_tasks(tasks, completion_status="completed")

    assert [task.task_id for task in filtered] == ["t-completed"]


def test_filter_tasks_by_pet_name_and_status() -> None:
    """Scheduler should filter tasks by pet name and combine with status filter."""
    scheduler = Scheduler()
    owner = Owner(owner_id="owner-1", name="Alex", daily_time_available_min=60)
    dog = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")
    cat = Pet(pet_id="pet-2", name="Luna", species="cat", age_group="adult")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog_task = Task(
        task_id="t-dog",
        title="Dog task",
        category="exercise",
        duration_min=20,
        priority=3,
        status="pending",
    )
    cat_pending_task = Task(
        task_id="t-cat-pending",
        title="Cat pending task",
        category="feeding",
        duration_min=10,
        priority=2,
        status="pending",
    )
    cat_completed_task = Task(
        task_id="t-cat-completed",
        title="Cat completed task",
        category="medical",
        duration_min=10,
        priority=4,
        status="completed",
    )

    dog.add_task(dog_task)
    cat.add_task(cat_pending_task)
    cat.add_task(cat_completed_task)
    tasks = [dog_task, cat_pending_task, cat_completed_task]

    pet_filtered = scheduler.filter_tasks(tasks, owner=owner, pet_name="Luna")
    combined_filtered = scheduler.filter_tasks(
        tasks,
        owner=owner,
        pet_name="Luna",
        completion_status="completed",
    )

    assert [task.task_id for task in pet_filtered] == ["t-cat-pending", "t-cat-completed"]
    assert [task.task_id for task in combined_filtered] == ["t-cat-completed"]


def test_detect_schedule_conflicts_warns_for_same_pet_overlap() -> None:
    """Overlap for one pet should produce a non-fatal warning."""
    scheduler = Scheduler()
    task_1 = Task(
        task_id="t-1",
        title="Morning walk",
        category="exercise",
        duration_min=30,
        priority=3,
    )
    task_2 = Task(
        task_id="t-2",
        title="Vet check",
        category="medical",
        duration_min=20,
        priority=4,
    )

    items = [
        PlannedItem(
            pet_id="pet-1",
            pet_name="Milo",
            task=task_1,
            start_minute_of_day=60,
            end_minute_of_day=90,
            reason_selected="test",
        ),
        PlannedItem(
            pet_id="pet-1",
            pet_name="Milo",
            task=task_2,
            start_minute_of_day=75,
            end_minute_of_day=95,
            reason_selected="test",
        ),
    ]

    warnings = scheduler.detect_schedule_conflicts(items)

    assert len(warnings) == 1
    assert "Warning:" in warnings[0]
    assert "same pet" in warnings[0]


def test_detect_schedule_conflicts_warns_for_cross_pet_overlap() -> None:
    """Overlap across pets should produce a cross-pet warning."""
    scheduler = Scheduler()
    task_1 = Task(
        task_id="t-a",
        title="Feed Milo",
        category="feeding",
        duration_min=15,
        priority=2,
    )
    task_2 = Task(
        task_id="t-b",
        title="Feed Luna",
        category="feeding",
        duration_min=15,
        priority=2,
    )

    items = [
        PlannedItem(
            pet_id="pet-1",
            pet_name="Milo",
            task=task_1,
            start_minute_of_day=120,
            end_minute_of_day=140,
            reason_selected="test",
        ),
        PlannedItem(
            pet_id="pet-2",
            pet_name="Luna",
            task=task_2,
            start_minute_of_day=130,
            end_minute_of_day=145,
            reason_selected="test",
        ),
    ]

    warnings = scheduler.detect_schedule_conflicts(items)

    assert len(warnings) == 1
    assert "Warning:" in warnings[0]
    assert "cross-pet" in warnings[0]


def test_sort_tasks_by_time_tiebreaks_same_due_by_score() -> None:
    """For equal due_by values, higher score should sort first."""
    scheduler = Scheduler()
    owner = Owner(owner_id="owner-1", name="Alex", daily_time_available_min=120)
    pet = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")
    owner.add_pet(pet)
    due = datetime(2026, 4, 1, 12, 0)

    low_score = Task(
        task_id="t-low",
        title="Lower score task",
        category="feeding",
        duration_min=20,
        priority=1,
        due_by=due,
        pet_id=pet.pet_id,
    )
    high_score = Task(
        task_id="t-high",
        title="Higher score task",
        category="feeding",
        duration_min=20,
        priority=5,
        due_by=due,
        pet_id=pet.pet_id,
    )

    sorted_tasks = scheduler.sort_tasks_by_time(
        [low_score, high_score],
        owner=owner,
        pet_by_id={pet.pet_id: pet},
    )

    assert [task.task_id for task in sorted_tasks] == ["t-high", "t-low"]


def test_sort_tasks_by_time_tiebreaks_same_due_and_score_by_task_id() -> None:
    """For equal due_by and score, lexical task_id should break ties."""
    scheduler = Scheduler()
    due = datetime(2026, 4, 1, 18, 0)
    tasks = [
        Task(
            task_id="t-b",
            title="Task B",
            category="feeding",
            duration_min=10,
            priority=3,
            due_by=due,
        ),
        Task(
            task_id="t-a",
            title="Task A",
            category="feeding",
            duration_min=10,
            priority=3,
            due_by=due,
        ),
    ]

    sorted_tasks = scheduler.sort_tasks_by_time(tasks)

    assert [task.task_id for task in sorted_tasks] == ["t-a", "t-b"]


def test_mark_complete_non_recurring_does_not_spawn_next_occurrence() -> None:
    """Completing a non-recurring task should not create a follow-up task."""
    pet = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")
    task = Task(
        task_id="task-once",
        title="One-time vaccine",
        category="medical",
        duration_min=30,
        priority=4,
        recurrence="once",
        due_by=datetime(2026, 4, 2, 9, 0),
    )
    pet.add_task(task)

    next_task = task.mark_complete(pet=pet)

    assert task.status == "completed"
    assert next_task is None
    assert len(pet.tasks) == 1


def test_mark_complete_already_completed_task_is_idempotent() -> None:
    """Completing an already completed task should be a no-op."""
    pet = Pet(pet_id="pet-1", name="Milo", species="dog", age_group="adult")
    task = Task(
        task_id="task-daily-idempotent",
        title="Daily check",
        category="medical",
        duration_min=10,
        priority=2,
        recurrence="daily",
        due_by=datetime(2026, 4, 3, 8, 0),
    )
    pet.add_task(task)

    first_next = task.mark_complete(pet=pet)
    second_next = task.mark_complete(pet=pet)

    assert first_next is not None
    assert second_next is None
    assert len(pet.tasks) == 2


def test_detect_schedule_conflicts_no_warning_for_touching_boundaries() -> None:
    """Tasks that touch at boundaries should not be treated as overlapping."""
    scheduler = Scheduler()
    task_1 = Task(
        task_id="t-1",
        title="Task 1",
        category="exercise",
        duration_min=30,
        priority=3,
    )
    task_2 = Task(
        task_id="t-2",
        title="Task 2",
        category="feeding",
        duration_min=20,
        priority=2,
    )

    items = [
        PlannedItem(
            pet_id="pet-1",
            pet_name="Milo",
            task=task_1,
            start_minute_of_day=60,
            end_minute_of_day=90,
            reason_selected="test",
        ),
        PlannedItem(
            pet_id="pet-1",
            pet_name="Milo",
            task=task_2,
            start_minute_of_day=90,
            end_minute_of_day=110,
            reason_selected="test",
        ),
    ]

    warnings = scheduler.detect_schedule_conflicts(items)

    assert warnings == []
