from dataclasses import dataclass, field
from typing import Optional

PRIORITY_LEVELS = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str        # "low", "medium", "high"
    category: str        # "walk", "feed", "meds", "grooming", "enrichment"
    frequency: str       # "daily", "weekly", "as-needed"
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True

    def is_high_priority(self) -> bool:
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        self.tasks = [t for t in self.tasks if t.title != title]

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def get_profile(self) -> str:
        return f"{self.name} ({self.species}, age {self.age}) — {len(self.tasks)} task(s)"


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: Optional[str] = None
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        self.pets = [p for p in self.pets if p.name != name]

    def get_all_tasks(self) -> list[Task]:
        """Aggregate tasks from every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks

    def get_available_time(self) -> int:
        return self.available_minutes

    def update_preferences(self, pref: str) -> None:
        self.preferences = pref


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def build_plan(self) -> None:
        """
        Retrieve all tasks from the owner's pets, sort by priority (high first),
        then greedily fill the time budget. Incomplete tasks only.
        """
        self.scheduled_tasks = []
        self.skipped_tasks = []

        all_tasks = self.owner.get_all_tasks()
        pending = [t for t in all_tasks if not t.completed]
        pending.sort(
            key=lambda t: PRIORITY_LEVELS.get(t.priority, 0),
            reverse=True,
        )

        time_remaining = self.owner.get_available_time()
        for task in pending:
            if task.duration_minutes <= time_remaining:
                self.scheduled_tasks.append(task)
                time_remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)

    def get_skipped_tasks(self) -> list[Task]:
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
