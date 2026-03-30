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
# Section 3: Add a task
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
        col4, col5, col6 = st.columns(3)
        with col4:
            category = st.selectbox("Category", ["walk", "feed", "meds", "grooming", "enrichment"])
        with col5:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        with col6:
            scheduled_time = st.text_input("Start time (HH:MM)", value="", placeholder="07:00")
        task_submitted = st.form_submit_button("Add task")

    if task_submitted:
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(
            task_title, int(duration), priority, category, frequency,
            scheduled_time=scheduled_time.strip() or None,
        ))
        st.success(f"Added '{task_title}' to {selected_pet_name}'s tasks.")

    for pet in owner.pets:
        tasks = pet.get_tasks()
        if tasks:
            st.markdown(f"**{pet.name}'s tasks**")
            st.table([
                {
                    "Title": t.title,
                    "Start": t.scheduled_time or "—",
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Category": t.category,
                    "Frequency": t.frequency,
                    "Done": "Yes" if t.completed else "No",
                }
                for t in tasks
            ])

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule", disabled=not owner.pets):
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    st.session_state.scheduler = scheduler

if "scheduler" in st.session_state:
    s: Scheduler = st.session_state.scheduler

    # --- Conflict warnings ------------------------------------------------
    # Shown before the plan so the owner can fix issues before acting on it.
    # Time conflicts get st.warning (actionable but not blocking).
    # Time overload gets st.error (more severe — daily tasks won't all fit).
    conflicts = s.detect_conflicts()
    if conflicts:
        st.markdown("#### Scheduling Alerts")
        for msg in conflicts:
            if "overload" in msg.lower():
                st.error(f"🚨 {msg}")
            else:
                st.warning(f"⚠️ {msg}")
    else:
        st.success("No conflicts detected — your schedule looks clean!")

    # --- Sorted schedule table --------------------------------------------
    st.markdown("#### Today's Schedule")

    # Filter controls — let the owner focus on one pet or category
    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox(
            "Filter by pet",
            ["All"] + [p.name for p in owner.pets],
            key="filter_pet",
        )
    with col2:
        filter_cat = st.selectbox(
            "Filter by category",
            ["All", "walk", "feed", "meds", "grooming", "enrichment"],
            key="filter_cat",
        )

    sorted_tasks = s.sort_by_time()

    # Apply filters using filter_scheduled on the scheduler, then intersect
    # with the sort order so chronological order is preserved.
    filtered = s.filter_scheduled(
        pet_name=filter_pet if filter_pet != "All" else None,
        category=filter_cat if filter_cat != "All" else None,
    )
    filtered_ids = {id(t) for t in filtered}
    display_tasks = [t for t in sorted_tasks if id(t) in filtered_ids]

    if display_tasks:
        total_shown = sum(t.duration_minutes for t in display_tasks)
        st.caption(f"{len(display_tasks)} task(s) shown · {total_shown} min")
        st.table([
            {
                "Start": t.scheduled_time or "—",
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Category": t.category,
                "Frequency": t.frequency,
                "Status": "Done" if t.completed else "Pending",
            }
            for t in display_tasks
        ])
    else:
        st.info("No tasks match the current filters.")

    # --- Skipped tasks ----------------------------------------------------
    skipped = s.get_skipped_tasks()
    if skipped:
        with st.expander(f"Skipped tasks ({len(skipped)}) — didn't fit in the time budget"):
            st.table([
                {
                    "Task": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                    "Frequency": t.frequency,
                }
                for t in skipped
            ])

    # --- Reasoning --------------------------------------------------------
    with st.expander("Why were these tasks chosen?"):
        st.text(s.explain_plan())
