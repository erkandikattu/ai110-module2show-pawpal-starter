"""Demo script for generating and printing today's PawPal schedule."""

from datetime import date, datetime, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


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


if __name__ == "__main__":
	sample_owner = build_sample_owner()
	print_plan_for_today(sample_owner)
