from dataclasses import dataclass, field
from typing import Optional

PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3}

# Lower number = scheduled earlier. daily tasks always come before weekly/as-needed.
FREQUENCY_ORDER = {"daily": 0, "weekly": 1, "as-needed": 2}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str        # "low", "medium", "high"
    category: str        # "walk", "feed", "meds", "grooming", "enrichment"
    frequency: str       # "daily", "weekly", "as-needed"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is high."""
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove all tasks matching the given title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> list[Task]:
        """Return the pet's full task list."""
        return self.tasks

    def get_profile(self) -> str:
        """Return a one-line summary of the pet's profile and task count."""
        return f"{self.name} ({self.species}, age {self.age}) — {len(self.tasks)} task(s)"


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: Optional[str] = None
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove all pets matching the given name."""
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> list[Task]:
        """Aggregate tasks from every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_available_time(self) -> int:
        """Return the number of minutes the owner has available today."""
        return self.available_minutes

    def update_preferences(self, pref: str) -> None:
        """Update the owner's care preferences."""
        self.preferences = pref


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def build_plan(self) -> None:
        """
        Sort pending tasks by frequency (daily first), then priority (high first),
        then duration (shortest first as tiebreaker). Greedily fill the time budget.
        """
        self.scheduled_tasks = []
        self.skipped_tasks = []

        all_tasks = self.owner.get_all_tasks()
        pending = [t for t in all_tasks if not t.completed]
        pending.sort(
            key=lambda t: (
                FREQUENCY_ORDER.get(t.frequency, 99),   # daily before weekly/as-needed
                -PRIORITY_LEVELS.get(t.priority, 0),    # high priority before low
                t.duration_minutes,                      # shorter tasks break ties
            )
        )

        time_remaining = self.owner.get_available_time()
        for task in pending:
            if task.duration_minutes <= time_remaining:
                self.scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)

    def filter_scheduled(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        category: str | None = None,
    ) -> list[Task]:
        """Return scheduled tasks filtered by pet name, completion status, or category."""
        # Build a lookup so we can match tasks back to their pet
        task_to_pet: dict[int, str] = {}
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                task_to_pet[id(task)] = pet.name

        results = self.scheduled_tasks
        if pet_name is not None:
            results = [t for t in results if task_to_pet.get(id(t)) == pet_name]
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        if category is not None:
            results = [t for t in results if t.category == category]
        return results

    def detect_conflicts(self) -> list[str]:
        """
        Scan for scheduling problems and return a list of plain-language warnings.

        Checks:
        - Duplicate task titles assigned to the same pet.
        - Total daily-task time exceeding the owner's available minutes.
        """
        warnings: list[str] = []

        # 1. Duplicate task titles per pet
        for pet in self.owner.pets:
            seen: set[str] = set()
            for task in pet.get_tasks():
                if task.title in seen:
                    warnings.append(
                        f"Conflict: '{task.title}' is listed more than once for {pet.name}."
                    )
                seen.add(task.title)

        # 2. Daily tasks alone exceed the available time budget
        all_tasks = self.owner.get_all_tasks()
        daily_total = sum(t.duration_minutes for t in all_tasks if t.frequency == "daily")
        budget = self.owner.get_available_time()
        if daily_total > budget:
            warnings.append(
                f"Time overload: daily tasks total {daily_total} min but only "
                f"{budget} min are available. Some daily tasks will be skipped."
            )

        return warnings

    def get_skipped_tasks(self) -> list[Task]:
        """Return tasks that did not fit within the available time budget."""
        return self.skipped_tasks

    def explain_plan(self) -> str:
        """Return a plain-language explanation of every scheduling decision."""
        lines = []
        for task in self.scheduled_tasks:
            lines.append(
                f"✔ '{task.title}' scheduled — {task.duration_minutes} min, "
                f"{task.priority} priority ({task.frequency})"
            )
        for task in self.skipped_tasks:
            lines.append(
                f"✘ '{task.title}' skipped — not enough time remaining "
                f"({task.duration_minutes} min needed)"
            )
        return "\n".join(lines) if lines else "No tasks to schedule."

    def display_plan(self) -> str:
        """Return a compact ordered schedule suitable for the UI."""
        if not self.scheduled_tasks:
            return "No tasks fit within the available time."
        lines = ["Daily Plan:"]
        for i, task in enumerate(self.scheduled_tasks, 1):
            status = "done" if task.completed else "pending"
            lines.append(
                f"  {i}. {task.title} — {task.duration_minutes} min "
                f"[{task.priority}] ({status})"
            )
        total = sum(t.duration_minutes for t in self.scheduled_tasks)
        lines.append(f"\nTotal time: {total} / {self.owner.available_minutes} min")
        return "\n".join(lines)
