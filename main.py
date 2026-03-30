from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=60, preferences="mornings preferred")

mochi = Pet(name="Mochi", species="dog", age=3)
mochi.add_task(Task("Morning walk",   20, "high",   "walk",       "daily"))
mochi.add_task(Task("Feeding",        10, "high",   "feed",       "daily"))
mochi.add_task(Task("Medication",      5, "high",   "meds",       "daily"))
mochi.add_task(Task("Grooming",       45, "medium", "grooming",   "weekly"))
mochi.add_task(Task("Feeding",        10, "high",   "feed",       "daily"))  # intentional duplicate

luna = Pet(name="Luna", species="cat", age=5)
luna.add_task(Task("Feeding",         10, "high",   "feed",       "daily"))
luna.add_task(Task("Litter cleaning", 15, "medium", "enrichment", "daily"))
luna.add_task(Task("Playtime",        20, "low",    "enrichment", "as-needed"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner)

# --- Conflict detection (before building the plan) ---
print("=" * 40)
print("  Conflict Detection")
print("=" * 40)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(f"  ⚠  {c}")
else:
    print("  No conflicts detected.")
print()

# --- Build plan (frequency + priority + duration sort) ---
scheduler.build_plan()

print("=" * 40)
print(f"  Today's Schedule for {owner.name}")
print("=" * 40)
print(scheduler.display_plan())
print()

print("--- Reasoning ---")
print(scheduler.explain_plan())
print()

# --- Filter: Mochi's tasks only ---
print("--- Filter: Mochi's scheduled tasks ---")
mochi_tasks = scheduler.filter_scheduled(pet_name="Mochi")
for t in mochi_tasks:
    print(f"  {t.title} ({t.duration_minutes} min, {t.priority})")
print()

# --- Filter: pending tasks only ---
print("--- Filter: pending (not yet done) ---")
pending = scheduler.filter_scheduled(completed=False)
for t in pending:
    print(f"  {t.title}")
print()

# --- Filter: feed category ---
print("--- Filter: feed tasks ---")
feed_tasks = scheduler.filter_scheduled(category="feed")
for t in feed_tasks:
    print(f"  {t.title}")
