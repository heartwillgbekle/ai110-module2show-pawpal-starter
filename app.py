import streamlit as st
from datetime import datetime, time
from pawpal_system import load_dummy_data, Task, Pet

# ------------------------------------------------------------------------------
# SETUP & STATE
# ------------------------------------------------------------------------------
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

if 'scheduler' not in st.session_state:
    st.session_state.scheduler = load_dummy_data()

scheduler = st.session_state.scheduler

# ------------------------------------------------------------------------------
# SIDEBAR: ADD ACTIONS
# ------------------------------------------------------------------------------
st.sidebar.title("🐾 PawPal+")
st.sidebar.subheader("Quick Actions")

# Add New Pet
with st.sidebar.expander("Add New Pet"):
    with st.form("new_pet_form"):
        p_name = st.text_input("Name")
        p_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
        p_age = st.number_input("Age", min_value=0, max_value=30)
        p_submit = st.form_submit_button("Add Pet")
        
        if p_submit and p_name:
            new_id = len(scheduler.pets) + 1
            scheduler.add_pet(Pet(new_id, p_name, p_species, p_age))
            st.success(f"Added {p_name}!")
            st.rerun()

# Add New Task
with st.sidebar.expander("Schedule Task", expanded=True):
    if not scheduler.pets:
        st.write("Add a pet first!")
    else:
        with st.form("new_task_form"):
            target_pet_name = st.selectbox("For", [p.name for p in scheduler.pets])
            t_desc = st.text_input("Task (e.g., Walk)")
            t_time = st.time_input("Time", datetime.now().time())
            t_dur = st.slider("Duration (mins)", 5, 60, 15)
            t_freq = st.selectbox("Frequency", ["Once", "Daily", "Weekly"])
            t_submit = st.form_submit_button("Schedule")

            if t_submit and t_desc:
                # Find the pet object
                target_pet = next(p for p in scheduler.pets if p.name == target_pet_name)
                
                # Construct datetime (using today's date + selected time)
                due_dt = datetime.combine(datetime.today(), t_time)
                new_task = Task(len(target_pet.tasks)+100, t_desc, due_dt, t_dur, frequency=t_freq)

                # CALL STUDENT LOGIC: Conflict Check
                if scheduler.check_conflicts(new_task):
                    st.error("⚠️ Conflict detected! You have another task at this time.")
                else:
                    target_pet.add_task(new_task)
                    st.success("Task Scheduled!")
                    st.rerun()

# ------------------------------------------------------------------------------
# MAIN DASHBOARD
# ------------------------------------------------------------------------------
st.title("Today's Schedule")

# Metrics
col1, col2 = st.columns(2)
col1.metric("Pets Managed", len(scheduler.pets))
col2.metric("Pending Tasks", len([t for _, t in scheduler.get_all_tasks() if not t.is_completed]))

st.divider()

tasks = scheduler.get_upcoming_tasks()

if not tasks:
    st.info("No upcoming tasks! Relax with your furry friends. 🛋️")
else:
    for pet_name, task in tasks:
        # Visual styling based on completion
        card_color = "green" if task.is_completed else "blue"
        opacity = 0.5 if task.is_completed else 1.0
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 4, 1])
            
            with c1:
                st.write(f"**{task.due_time.strftime('%I:%M %p')}**")
            
            with c2:
                if task.is_completed:
                    st.markdown(f"~~{pet_name}: {task.description}~~")
                else:
                    st.markdown(f"**{pet_name}**: {task.description}")
                st.caption(f"{task.duration_mins} mins | {task.frequency}")
            
            with c3:
                if not task.is_completed:
                    if st.button("Done", key=f"done_{task.id}"):
                        task.mark_complete()
                        st.rerun()
                else:
                    st.write("✅")

# ------------------------------------------------------------------------------
# DEBUG / INSPECTOR
# ------------------------------------------------------------------------------
with st.expander("Debug: Raw System Data"):
    st.write(scheduler.pets)
