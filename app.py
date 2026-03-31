import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

# Keep domain classes imported and discoverable for upcoming scheduler wiring.
_PAWPAL_DOMAIN_CLASSES = (Owner, Pet, Task, Scheduler)

_PRIORITY_TO_SCORE = {"low": 1, "medium": 2, "high": 3}


def _ensure_session_objects() -> None:
    """Initialize long-lived domain objects in session state once per user session."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(
            owner_id="owner-1",
            name="Jordan",
            daily_time_available_min=120,
            preferred_time_windows=["morning", "afternoon"],
        )

    if "pet" not in st.session_state:
        st.session_state.pet = Pet(
            pet_id="pet-1",
            name="Mochi",
            species="dog",
            age_group="adult",
        )

    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler()

    if "tasks" not in st.session_state:
        st.session_state.tasks = st.session_state.pet.tasks

    if "task_counter" not in st.session_state:
        st.session_state.task_counter = len(st.session_state.tasks)

    if "pet_counter" not in st.session_state:
        st.session_state.pet_counter = len(st.session_state.owner.pets)

    if "last_plan" not in st.session_state:
        st.session_state.last_plan = None

    owner_obj = st.session_state.owner
    pet_obj = st.session_state.pet
    if not any(existing_pet.pet_id == pet_obj.pet_id for existing_pet in owner_obj.pets):
        owner_obj.add_pet(pet_obj)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
_ensure_session_objects()

owner = st.session_state.owner

pet_lookup = {existing_pet.pet_id: existing_pet for existing_pet in owner.pets}
pet_ids = list(pet_lookup.keys())
default_pet_index = pet_ids.index(st.session_state.pet.pet_id) if st.session_state.pet.pet_id in pet_ids else 0
selected_pet_id = st.selectbox(
    "Active pet",
    options=pet_ids,
    index=default_pet_index,
    format_func=lambda pet_id: f"{pet_lookup[pet_id].name} ({pet_lookup[pet_id].species})",
)
pet = pet_lookup[selected_pet_id]
st.session_state.pet = pet

owner_name = st.text_input("Owner name", value=owner.name)
pet_name = st.text_input("Pet name", value=pet.name)
species_options = ["dog", "cat", "other"]
species_default_index = species_options.index(pet.species) if pet.species in species_options else 0
species = st.selectbox("Species", species_options, index=species_default_index)

# Keep object fields in sync with the latest form values.
owner.name = owner_name.strip() or owner.name
pet.name = pet_name.strip() or pet.name
pet.species = species

st.markdown("### Add a Pet")
st.caption("Create a new pet profile and add it to this owner using Owner.add_pet().")

pet_col1, pet_col2, pet_col3 = st.columns(3)
with pet_col1:
    new_pet_name = st.text_input("New pet name", value="", placeholder="Luna")
with pet_col2:
    new_pet_species = st.selectbox("New pet species", species_options, index=0)
with pet_col3:
    age_group = st.selectbox("Age group", ["young", "adult", "senior"], index=1)

if st.button("Add pet"):
    if not new_pet_name.strip():
        st.warning("Enter a pet name before adding a pet.")
    else:
        st.session_state.pet_counter += 1
        new_pet = Pet(
            pet_id=f"pet-{st.session_state.pet_counter}",
            name=new_pet_name.strip(),
            species=new_pet_species,
            age_group=age_group,
        )
        owner.add_pet(new_pet)
        st.session_state.pet = new_pet
        st.success(f"Added {new_pet.name} to {owner.name}'s pets.")

st.markdown("### Schedule a Task")
st.caption("Create a task and attach it to the active pet using Pet.add_task().")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.task_counter += 1
    task = Task(
        task_id=f"task-{st.session_state.task_counter}",
        title=task_title.strip() or f"Task {st.session_state.task_counter}",
        category="general",
        duration_min=int(duration),
        priority=_PRIORITY_TO_SCORE[priority],
        preferred_windows=owner.preferred_time_windows.copy(),
    )
    pet.add_task(task)

if pet.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "id": task.task_id,
                "title": task.title,
                "duration_minutes": task.duration_min,
                "priority": task.priority,
                "status": task.status,
            }
            for task in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily plan with Scheduler.generate_owner_daily_plan().")

if st.button("Generate schedule"):
    if not pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        st.session_state.last_plan = st.session_state.scheduler.generate_owner_daily_plan(
            owner,
            date.today(),
        )

if st.session_state.last_plan is not None:
    plan = st.session_state.last_plan
    st.success(plan.summary())
    if plan.explanations:
        st.markdown("### Plan Details")
        for explanation in plan.explanations:
            st.write(f"- {explanation}")
