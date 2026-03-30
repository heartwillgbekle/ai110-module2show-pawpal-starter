from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90, preferences="mornings preferred")

mochi = Pet(name="Mochi", species="dog", age=3)
# Morning walk starts at 07:00 and lasts 20 min → window 07:00–07:20
mochi.add_task(Task("Morning walk", 20, "high",   "walk",     "daily",  scheduled_time="07:00", due_date=date.today()))
# Feeding starts at 07:10 — intentional overlap with morning walk (07:00–07:20)
mochi.add_task(Task("Feeding",      10, "high",   "feed",     "daily",  scheduled_time="07:10", due_date=date.today()))
mochi.add_task(Task("Medication",    5, "high",   "meds",     "daily",  scheduled_time="08:00", due_date=date.today()))
mochi.add_task(Task("Grooming",     30, "medium", "grooming", "weekly", scheduled_time="10:00", due_date=date.today()))

luna = Pet(name="Luna", species="cat", age=5)
# Litter cleaning starts at 08:00 and lasts 15 min → window 08:00–08:15
luna.add_task(Task("Feeding",        10, "high",   "feed",      "daily",      scheduled_time="07:45", due_date=date.today()))
luna.add_task(Task("Litter cleaning",15, "medium", "enrichment","daily",      scheduled_time="08:00", due_date=date.today()))
# Playtime starts at 08:05 — overlaps with litter cleaning (08:00–08:15)
luna.add_task(Task("Playtime",       20, "low",    "enrichment","as-needed",  scheduled_time="08:05"))

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner)
scheduler.build_plan()

# --- Conflict detection (after build so time-overlap check has scheduled_tasks) ---
print("=" * 52)
print("  Conflict Detection")
print("=" * 52)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(f"  ⚠  {c}")
else:
    print("  No conflicts detected.")
print()

# --- Schedule sorted by time ---
print("=" * 52)
print(f"  Today's Schedule — {owner.name}")
print("=" * 52)
print(scheduler.display_plan())
print()
print("Sorted by start time:")
for t in scheduler.sort_by_time():
    time_label = t.scheduled_time or "—"
    print(f"  {time_label}  {t.title:<20} {t.duration_minutes} min  [{t.priority}]")
