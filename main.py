from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90, preferences="mornings preferred")

# Tasks added OUT OF ORDER by time to prove sort_by_time() works
mochi = Pet(name="Mochi", species="dog", age=3)
mochi.add_task(Task("Evening walk",   20, "medium", "walk",     "daily",      scheduled_time="18:00"))
mochi.add_task(Task("Medication",      5, "high",   "meds",     "daily",      scheduled_time="08:30"))
mochi.add_task(Task("Morning walk",   20, "high",   "walk",     "daily",      scheduled_time="07:00"))
mochi.add_task(Task("Feeding",        10, "high",   "feed",     "daily",      scheduled_time="07:30"))
mochi.add_task(Task("Grooming",       30, "medium", "grooming", "weekly",     scheduled_time="10:00"))

luna = Pet(name="Luna", species="cat", age=5)
luna.add_task(Task("Feeding",         10, "high",   "feed",     "daily",      scheduled_time="07:45"))
luna.add_task(Task("Litter cleaning", 15, "medium", "enrichment","daily",     scheduled_time="09:00"))
luna.add_task(Task("Playtime",        20, "low",    "enrichment","as-needed")) # no time set

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner)

# --- Conflict detection ---
print("=" * 44)
print("  Conflict Detection")
print("=" * 44)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(f"  ⚠  {c}")
else:
    print("  No conflicts detected.")
print()

# --- Build plan ---
scheduler.build_plan()

# --- Sort by time ---
print("=" * 44)
print("  Schedule sorted by start time (HH:MM)")
print("=" * 44)
for task in scheduler.sort_by_time():
    time_label = task.scheduled_time or "no time set"
    print(f"  {time_label}  {task.title:<20} {task.duration_minutes} min  [{task.priority}]")
print()

# --- Filter: Mochi's tasks ---
print("--- Filter: Mochi's scheduled tasks ---")
for t in scheduler.filter_scheduled(pet_name="Mochi"):
    print(f"  {t.title} ({t.scheduled_time or '—'})")
print()

# --- Filter: pending tasks ---
print("--- Filter: not yet completed ---")
for t in scheduler.filter_scheduled(completed=False):
    print(f"  {t.title}")
print()

# --- Filter: feed category ---
print("--- Filter: feed tasks only ---")
for t in scheduler.filter_scheduled(category="feed"):
    print(f"  {t.title} @ {t.scheduled_time or '—'}")
print()

# --- Full plan + reasoning ---
print("=" * 44)
print(f"  Full Plan — {owner.name}")
print("=" * 44)
print(scheduler.display_plan())
print()
print("--- Reasoning ---")
print(scheduler.explain_plan())
