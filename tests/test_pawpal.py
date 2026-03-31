"""Unit tests for core PawPal behaviors."""

from pawpal_system import Pet, Task


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
