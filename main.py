from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", available_minutes=90, preferences="mornings preferred")

mochi = Pet(name="Mochi", species="dog", age=3)
mochi.add_task(Task("Morning walk", 20, "high",   "walk",     "daily",  scheduled_time="07:00", due_date=date.today()))
mochi.add_task(Task("Feeding",      10, "high",   "feed",     "daily",  scheduled_time="07:30", due_date=date.today()))
mochi.add_task(Task("Medication",    5, "high",   "meds",     "daily",  scheduled_time="08:30", due_date=date.today()))
mochi.add_task(Task("Grooming",     30, "medium", "grooming", "weekly", scheduled_time="10:00", due_date=date.today()))

luna = Pet(name="Luna", species="cat", age=5)
luna.add_task(Task("Feeding",        10, "high",   "feed",      "daily",      scheduled_time="07:45", due_date=date.today()))
luna.add_task(Task("Litter cleaning",15, "medium", "enrichment","daily",      scheduled_time="09:00", due_date=date.today()))
luna.add_task(Task("Playtime",       20, "low",    "enrichment","as-needed"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Demo: complete a daily task → next occurrence auto-created ---
print("=" * 50)
print("  Recurring Task Demo")
print("=" * 50)

print(f"\nMochi's tasks BEFORE completing 'Morning walk' ({len(mochi.get_tasks())} total):")
for t in mochi.get_tasks():
    status = "✔" if t.completed else "○"
    print(f"  {status} {t.title:<20} due: {t.due_date}  freq: {t.frequency}")

next_walk = mochi.complete_task("Morning walk")
print(f"\nMarked 'Morning walk' complete.")
if next_walk:
    print(f"Next occurrence auto-created → due: {next_walk.due_date} (today + 1 day via timedelta)")

print(f"\nMochi's tasks AFTER ({len(mochi.get_tasks())} total):")
for t in mochi.get_tasks():
    status = "✔" if t.completed else "○"
    print(f"  {status} {t.title:<20} due: {t.due_date}  freq: {t.frequency}")

# --- Demo: complete a weekly task → next occurrence 7 days out ---
print()
next_groom = mochi.complete_task("Grooming")
print(f"Marked 'Grooming' (weekly) complete.")
if next_groom:
    print(f"Next occurrence auto-created → due: {next_groom.due_date} (today + 7 days via timedelta)")

# --- Demo: complete an as-needed task → no recurrence ---
print()
result = luna.complete_task("Playtime")
print(f"Marked 'Playtime' (as-needed) complete.")
print(f"Next occurrence created: {result is not None}  ← as-needed tasks do not recur")

# --- Build and display today's schedule ---
print()
print("=" * 50)
print(f"  Today's Schedule for {owner.name}")
print("=" * 50)
scheduler = Scheduler(owner)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for c in conflicts:
        print(f"  ⚠  {c}")
scheduler.build_plan()
print(scheduler.display_plan())
print()
print("Sorted by start time:")
for t in scheduler.sort_by_time():
    time_label = t.scheduled_time or "—"
    due = f"(due {t.due_date})" if t.due_date else ""
    print(f"  {time_label}  {t.title:<20} {t.duration_minutes} min  [{t.priority}]  {due}")
