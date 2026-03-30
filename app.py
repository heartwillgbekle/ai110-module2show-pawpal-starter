import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state — created once on first load, reused on every rerun
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", available_minutes=60)

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1: Owner profile
# ---------------------------------------------------------------------------
st.subheader("Owner Info")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name or "Jordan")
with col2:
    owner.available_minutes = st.number_input(
        "Minutes available today", min_value=10, max_value=480, value=owner.available_minutes
    )

st.divider()

# ---------------------------------------------------------------------------
# Section 2: Add a pet
# Submitting this form calls owner.add_pet(), which stores the new Pet inside
# the Owner object in session state. Streamlit reruns after submit, so the
# updated owner.pets list is immediately reflected in the pet selector below.
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        new_pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        new_age = st.number_input("Age", min_value=0, max_value=30, value=1)
    submitted = st.form_submit_button("Add pet")

if submitted:
    existing_names = [p.name for p in owner.pets]
    if new_pet_name in existing_names:
        st.warning(f"A pet named '{new_pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=new_pet_name, species=new_species, age=int(new_age)))
        st.success(f"Added {new_pet_name} to {owner.name}'s pets!")

if owner.pets:
    st.write("Registered pets: " + ", ".join(p.get_profile() for p in owner.pets))

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add a task to a specific pet
# The user picks which pet gets the task from a dropdown built from
# owner.pets. On submit, pet.add_task() is called directly on the chosen
# Pet object stored inside the Owner — no syncing needed.
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before creating tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        col4, col5 = st.columns(2)
        with col4:
            category = st.selectbox("Category", ["walk", "feed", "meds", "grooming", "enrichment"])
        with col5:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        # Retrieve the exact Pet object from owner.pets and call add_task() on it
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(task_title, int(duration), priority, category, frequency))
        st.success(f"Added '{task_title}' to {selected_pet_name}'s tasks.")

    # Show all tasks grouped by pet
    for pet in owner.pets:
        tasks = pet.get_tasks()
        if tasks:
            st.markdown(f"**{pet.name}'s tasks**")
            st.table([
                {
                    "Title": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Category": t.category,
                    "Frequency": t.frequency,
                    "Done": t.completed,
                }
                for t in tasks
            ])

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# Scheduler.build_plan() pulls all tasks from owner.get_all_tasks(), which
# aggregates across every pet. The result is stored in session state so the
# plan stays visible even after subsequent reruns.
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule", disabled=not owner.pets):
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    st.session_state.scheduler = scheduler

if "scheduler" in st.session_state:
    s: Scheduler = st.session_state.scheduler
    st.code(s.display_plan(), language=None)
    with st.expander("Why these tasks?"):
        st.text(s.explain_plan())
