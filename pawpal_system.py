from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: Optional[str] = None

    def get_available_time(self) -> int:
        pass

    def update_preferences(self, pref: str) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Owner

    def get_profile(self) -> str:
        pass


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str  # "walk", "feed", "meds", "grooming", "enrichment"
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def is_high_priority(self) -> bool:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def build_plan(self) -> None:
        pass

    def get_skipped_tasks(self) -> list[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def display_plan(self) -> str:
        pass
