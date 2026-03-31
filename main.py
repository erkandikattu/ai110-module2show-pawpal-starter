"""Demo script for generating and printing today's PawPal schedule."""

from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, PlannedItem, Scheduler, Task


def build_sample_owner() -> Owner:
	"""Create an owner with two pets and a set of sample tasks."""
	owner = Owner(
		owner_id="owner-1",
		name="Alex",
		daily_time_available_min=120,
		preferred_time_windows=["morning", "afternoon", "evening"],
	)

	dog = Pet(
		pet_id="pet-1",
		name="Milo",
		species="dog",
		age_group="adult",
	)
	cat = Pet(
		pet_id="pet-2",
		name="Luna",
		species="cat",
		age_group="adult",
	)

	now = datetime.now()

	dog.add_task(
		Task(
			task_id="task-1",
			title="Morning walk",
			category="exercise",
			duration_min=30,
			priority=5,
			recurrence="daily",
			preferred_windows=["morning"],
			due_by=now.replace(hour=9, minute=0, second=0, microsecond=0),
		)
	)

	dog.add_task(
		Task(
			task_id="task-2",
			title="Afternoon feeding",
			category="feeding",
			duration_min=15,
			priority=4,
			recurrence="daily",
			preferred_windows=["afternoon"],
			due_by=now.replace(hour=13, minute=0, second=0, microsecond=0),
		)
	)

	cat.add_task(
		Task(
			task_id="task-3",
			title="Evening litter cleanup",
			category="hygiene",
			duration_min=20,
			priority=4,
			recurrence="daily",
			preferred_windows=["evening"],
			due_by=now.replace(hour=19, minute=0, second=0, microsecond=0),
		)
	)

	cat.add_task(
		Task(
			task_id="task-4",
			title="Medication",
			category="medical",
			duration_min=10,
			priority=2,
			recurrence="once",
			required=False,
			preferred_windows=["night"],
			due_by=now + timedelta(days=1),
		)
	)

	# Intentionally add tasks out of chronological order to test sorting behavior.
	cat.add_task(
		Task(
			task_id="task-5",
			title="Breakfast refill",
			category="feeding",
			duration_min=10,
			priority=3,
			recurrence="daily",
			preferred_windows=["morning"],
			due_by=now.replace(hour=8, minute=15, second=0, microsecond=0),
		)
	)

	dog.add_task(
		Task(
			task_id="task-6",
			title="Midday play",
			category="enrichment",
			duration_min=20,
			priority=3,
			recurrence="daily",
			preferred_windows=["afternoon"],
			due_by=now.replace(hour=15, minute=30, second=0, microsecond=0),
		)
	)

	dog.add_task(
		Task(
			task_id="task-7",
			title="Early water check",
			category="hygiene",
			duration_min=5,
			priority=2,
			recurrence="daily",
			preferred_windows=["morning"],
			due_by=now.replace(hour=7, minute=45, second=0, microsecond=0),
		)
	)

	owner.add_pet(dog)
	owner.add_pet(cat)
	return owner


def print_plan_for_today(owner: Owner) -> None:
	"""Generate and print today's schedule for all pets."""
	scheduler = Scheduler()
	today = date.today()
	plan = scheduler.generate_owner_daily_plan(owner, today)

	print("Today's Schedule")
	print(f"Date: {today.isoformat()}")
	print(f"Owner: {owner.name}")
	print("-" * 40)

	if not plan.items:
		print("No tasks scheduled for today.")
	else:
		for item in plan.items:
			start_h, start_m = divmod(item.start_minute_of_day, 60)
			end_h, end_m = divmod(item.end_minute_of_day, 60)
			print(
				f"{start_h:02d}:{start_m:02d}-{end_h:02d}:{end_m:02d} | "
				f"{item.pet_name}: {item.task.title} "
				f"({item.task.duration_min} min)"
			)

	print("-" * 40)
	print(f"Total scheduled: {plan.total_scheduled_min}/{plan.total_available_min} min")

	if plan.skipped_tasks:
		print("Skipped tasks:")
		for task in plan.skipped_tasks:
			pet_name = next((pet.name for pet in owner.pets if pet.pet_id == task.pet_id), "Unknown")
			print(f"- {pet_name}: {task.title} ({task.duration_min} min)")


def print_filter_and_sort_demo(owner: Owner) -> None:
	"""Print a quick terminal demo for filtering and time-based sorting."""
	scheduler = Scheduler()
	all_tasks = [task for pet in owner.pets for task in pet.tasks]
	pet_by_id = {pet.pet_id: pet for pet in owner.pets}

	# Mark one task complete to prove completion status filtering works.
	for task in all_tasks:
		if task.task_id == "task-4":
			task.status = "completed"
			break

	def _format_due(task: Task) -> str:
		return task.due_by.strftime("%H:%M") if task.due_by is not None else "None"

	print("\nFilter + Sort Demo")
	print("Input order:")
	for task in all_tasks:
		print(f"- {task.task_id} | {task.title} | pet={task.pet_id} | status={task.status} | due={_format_due(task)}")

	pending_tasks = scheduler.filter_tasks(all_tasks, owner=owner, completion_status="pending")
	pending_milo_tasks = scheduler.filter_tasks(
		all_tasks,
		owner=owner,
		completion_status="pending",
		pet_name="Milo",
	)
	sorted_pending_tasks = scheduler.sort_tasks_by_time(
		pending_tasks,
		owner=owner,
		pet_by_id=pet_by_id,
	)

	print("\nPending tasks (status filter):")
	for task in pending_tasks:
		print(f"- {task.task_id} | {task.title} | due={_format_due(task)}")

	print("\nPending tasks for Milo (status + pet filter):")
	for task in pending_milo_tasks:
		print(f"- {task.task_id} | {task.title} | due={_format_due(task)}")

	print("\nPending tasks sorted by time:")
	for task in sorted_pending_tasks:
		print(f"- {task.task_id} | {task.title} | due={_format_due(task)}")


def print_conflict_detection_demo(owner: Owner) -> None:
	"""Print a terminal demo that verifies conflict warnings are detected."""
	scheduler = Scheduler()
	dog = next((pet for pet in owner.pets if pet.name == "Milo"), owner.pets[0])
	cat = next((pet for pet in owner.pets if pet.name == "Luna"), owner.pets[-1])

	# Two overlapping items (09:00-09:30 and 09:15-09:40) to trigger conflict warnings.
	overlapping_items = [
		PlannedItem(
			pet_id=dog.pet_id,
			pet_name=dog.name,
			task=Task(
				task_id="conflict-1",
				title="Milo training",
				category="exercise",
				duration_min=30,
				priority=4,
				pet_id=dog.pet_id,
			),
			start_minute_of_day=9 * 60,
			end_minute_of_day=(9 * 60) + 30,
			reason_selected="Conflict demo item",
		),
		PlannedItem(
			pet_id=cat.pet_id,
			pet_name=cat.name,
			task=Task(
				task_id="conflict-2",
				title="Luna feeding",
				category="feeding",
				duration_min=25,
				priority=4,
				pet_id=cat.pet_id,
			),
			start_minute_of_day=(9 * 60) + 15,
			end_minute_of_day=(9 * 60) + 40,
			reason_selected="Conflict demo item",
		),
	]

	warnings = scheduler.detect_schedule_conflicts(overlapping_items)

	print("\nConflict Detection Demo")
	print("Planned overlapping items:")
	for item in overlapping_items:
		start_h, start_m = divmod(item.start_minute_of_day, 60)
		end_h, end_m = divmod(item.end_minute_of_day, 60)
		print(f"- {start_h:02d}:{start_m:02d}-{end_h:02d}:{end_m:02d} | {item.pet_name}: {item.task.title}")

	if warnings:
		print("Conflict warnings:")
		for warning in warnings:
			print(f"- {warning}")
	else:
		print("No conflict warnings detected.")


if __name__ == "__main__":
	sample_owner = build_sample_owner()
	print_plan_for_today(sample_owner)
	print_filter_and_sort_demo(sample_owner)
	print_conflict_detection_demo(sample_owner)
