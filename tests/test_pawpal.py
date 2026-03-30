from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner(minutes: int = 60) -> Owner:
    owner = Owner(name="Jordan", available_minutes=minutes)
    return owner


def make_pet(name: str = "Mochi") -> Pet:
    return Pet(name=name, species="dog", age=3)


def task(title: str, duration: int, priority: str = "high",
         category: str = "walk", frequency: str = "daily",
         scheduled_time: str | None = None) -> Task:
    return Task(title, duration, priority, category, frequency,
                scheduled_time=scheduled_time)


# ---------------------------------------------------------------------------
# Original tests (kept)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_task_status():
    t = task("Morning walk", 20)
    assert t.completed is False
    t.mark_complete()
    assert t.completed is True


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.get_tasks()) == 0
    pet.add_task(task("Feeding", 10))
    assert len(pet.get_tasks()) == 1
    pet.add_task(task("Grooming", 30, frequency="weekly"))
    assert len(pet.get_tasks()) == 2


# ---------------------------------------------------------------------------
# Happy path — Scheduler.build_plan
# ---------------------------------------------------------------------------

def test_build_plan_respects_time_budget():
    """Scheduled task durations must never exceed available_minutes."""
    owner = make_owner(minutes=30)
    pet = make_pet()
    pet.add_task(task("Walk", 20))
    pet.add_task(task("Feed", 10))
    pet.add_task(task("Groom", 15, priority="medium", frequency="weekly"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()

    total = sum(t.duration_minutes for t in s.scheduled_tasks)
    assert total <= owner.available_minutes


def test_build_plan_schedules_daily_before_weekly():
    """Daily tasks must appear in the plan before weekly ones."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Grooming", 20, priority="high", frequency="weekly"))
    pet.add_task(task("Feeding",  10, priority="medium", frequency="daily"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()

    titles = [t.title for t in s.scheduled_tasks]
    assert titles.index("Feeding") < titles.index("Grooming")


def test_build_plan_schedules_high_priority_first_within_same_frequency():
    """Among daily tasks, high priority must appear before low priority."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Low task",  10, priority="low",  frequency="daily"))
    pet.add_task(task("High task", 10, priority="high", frequency="daily"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()

    titles = [t.title for t in s.scheduled_tasks]
    assert titles.index("High task") < titles.index("Low task")


def test_build_plan_exactly_fills_budget():
    """A task that fills the budget exactly should be scheduled, not skipped."""
    owner = make_owner(minutes=20)
    pet = make_pet()
    pet.add_task(task("Walk", 20))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()

    assert len(s.scheduled_tasks) == 1
    assert len(s.skipped_tasks) == 0


def test_build_plan_skips_task_exceeding_budget():
    """A task longer than the available time must go to skipped_tasks."""
    owner = make_owner(minutes=15)
    pet = make_pet()
    pet.add_task(task("Long walk", 20))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()

    assert len(s.scheduled_tasks) == 0
    assert s.skipped_tasks[0].title == "Long walk"


# ---------------------------------------------------------------------------
# Edge cases — empty states
# ---------------------------------------------------------------------------

def test_build_plan_pet_with_no_tasks():
    """A pet with no tasks should produce an empty schedule without errors."""
    owner = make_owner()
    owner.add_pet(make_pet())

    s = Scheduler(owner)
    s.build_plan()

    assert s.scheduled_tasks == []
    assert s.skipped_tasks == []


def test_build_plan_owner_with_no_pets():
    """An owner with no pets should produce an empty schedule without errors."""
    s = Scheduler(make_owner())
    s.build_plan()

    assert s.scheduled_tasks == []


def test_build_plan_all_tasks_already_completed():
    """Completed tasks must never be re-scheduled."""
    owner = make_owner()
    pet = make_pet()
    t = task("Walk", 20)
    t.mark_complete()
    pet.add_task(t)
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()

    assert s.scheduled_tasks == []


# ---------------------------------------------------------------------------
# Recurring tasks
# ---------------------------------------------------------------------------

def test_next_occurrence_daily_is_tomorrow():
    """next_occurrence() on a daily task should set due_date to today + 1."""
    today = date.today()
    t = Task("Walk", 20, "high", "walk", "daily", due_date=today)
    nxt = t.next_occurrence()

    assert nxt is not None
    assert nxt.due_date == today + timedelta(days=1)
    assert nxt.completed is False


def test_next_occurrence_weekly_is_seven_days():
    """next_occurrence() on a weekly task should set due_date to today + 7."""
    today = date.today()
    t = Task("Grooming", 30, "medium", "grooming", "weekly", due_date=today)
    nxt = t.next_occurrence()

    assert nxt is not None
    assert nxt.due_date == today + timedelta(days=7)


def test_next_occurrence_as_needed_returns_none():
    """as-needed tasks must not recur — next_occurrence() returns None."""
    t = task("Playtime", 20, frequency="as-needed")
    assert t.next_occurrence() is None


def test_complete_task_appends_next_occurrence():
    """Completing a daily task should add a new pending instance to the pet."""
    pet = make_pet()
    pet.add_task(Task("Walk", 20, "high", "walk", "daily", due_date=date.today()))

    pet.complete_task("Walk")

    tasks = pet.get_tasks()
    assert len(tasks) == 2                   # original + next occurrence
    assert tasks[0].completed is True
    assert tasks[1].completed is False
    assert tasks[1].due_date == date.today() + timedelta(days=1)


def test_complete_task_as_needed_does_not_append():
    """Completing an as-needed task must not add a new occurrence."""
    pet = make_pet()
    pet.add_task(task("Playtime", 20, frequency="as-needed"))
    pet.complete_task("Playtime")

    assert len(pet.get_tasks()) == 1         # no new task appended


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_start_time():
    """Two tasks with the same start time should trigger a time conflict warning."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Walk",  20, scheduled_time="08:00"))
    pet.add_task(task("Feed",  10, scheduled_time="08:00"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()
    conflicts = s.detect_conflicts()

    assert any("Time conflict" in c for c in conflicts)


def test_detect_conflicts_overlapping_windows():
    """A task starting inside another's window should trigger a conflict."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Walk", 30, scheduled_time="07:00"))  # ends 07:30
    pet.add_task(task("Feed", 10, scheduled_time="07:15"))  # starts inside walk
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()
    conflicts = s.detect_conflicts()

    assert any("Time conflict" in c for c in conflicts)


def test_detect_conflicts_no_overlap():
    """Tasks that do not overlap should produce no time conflict warnings."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Walk", 20, scheduled_time="07:00"))  # ends 07:20
    pet.add_task(task("Feed", 10, scheduled_time="07:20"))  # starts exactly at end
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()
    conflicts = s.detect_conflicts()

    assert not any("Time conflict" in c for c in conflicts)


def test_detect_conflicts_duplicate_title():
    """Two incomplete tasks with the same title on one pet should warn."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Feed", 10))
    pet.add_task(task("Feed", 10))
    owner.add_pet(pet)

    s = Scheduler(owner)
    conflicts = s.detect_conflicts()

    assert any("more than once" in c for c in conflicts)


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_sort_by_time_chronological_order():
    """sort_by_time() must return tasks in HH:MM ascending order."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("Evening", 10, scheduled_time="18:00"))
    pet.add_task(task("Morning", 10, scheduled_time="07:00"))
    pet.add_task(task("Midday",  10, scheduled_time="12:00"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()
    sorted_titles = [t.title for t in s.sort_by_time()]

    assert sorted_titles == ["Morning", "Midday", "Evening"]


def test_sort_by_time_no_time_goes_last():
    """Tasks without a scheduled_time must sort after all timed tasks."""
    owner = make_owner(minutes=90)
    pet = make_pet()
    pet.add_task(task("No time", 10))                         # no scheduled_time
    pet.add_task(task("Morning", 10, scheduled_time="07:00"))
    owner.add_pet(pet)

    s = Scheduler(owner)
    s.build_plan()
    sorted_titles = [t.title for t in s.sort_by_time()]

    assert sorted_titles[-1] == "No time"
