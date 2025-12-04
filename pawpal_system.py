from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

# ------------------------------------------------------------------------------
# 1. CLASS DEFINITIONS
# ------------------------------------------------------------------------------

@dataclass
class Task:
    """Represents a single care activity."""
    id: int
    description: str
    due_time: datetime
    duration_mins: int = 15
    is_completed: bool = False
    frequency: str = "Once"  # Options: Once, Daily, Weekly

    def mark_complete(self):
        self.is_completed = True

@dataclass
class Pet:
    """Represents a pet profile."""
    id: int
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)

class Scheduler:
    """
    Manages scheduling logic, conflict detection, and task retrieval.
    This is the 'Brain' of the system.
    """
    def __init__(self):
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        self.pets.append(pet)

    def get_all_tasks(self) -> List[tuple[str, Task]]:
        """Helper: returns a list of (pet_name, task) tuples for easy display."""
        all_tasks = []
        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet.name, task))
        return all_tasks

    def get_upcoming_tasks(self) -> List[tuple[str, Task]]:
        """
        TODO: Ask AI to help design a sorting algorithm.
        """
        # <YOUR CODE HERE>
        return self.get_all_tasks() # Placeholder

    def check_conflicts(self, new_task: Task) -> bool:
        """
        TODO: Ask AI to help design a conflict detection algorithm.
        Return True if new_task overlaps with any existing task for ANY pet.
        (Assume a simple model: task start time -> start time + duration)
        """
        # <YOUR CODE HERE>
        return False # Placeholder

    def generate_recurring_tasks(self):
        """
        TODO: (Stretch) Ask AI how to handle recurring tasks.
        If a task is 'Daily', this logic should create the next instance.
        """
        pass

# ------------------------------------------------------------------------------
# 2. DATA SEEDING (For testing)
# ------------------------------------------------------------------------------
def load_dummy_data() -> Scheduler:
    scheduler = Scheduler()
    
    # Pet 1
    luna = Pet(1, "Luna", "Dog", 4)
    t1 = Task(101, "Morning Walk", datetime.now() + timedelta(hours=1), 30, frequency="Daily")
    t2 = Task(102, "Dinner", datetime.now() + timedelta(hours=6), 15, frequency="Daily")
    luna.add_task(t1)
    luna.add_task(t2)
    
    # Pet 2
    milo = Pet(2, "Milo", "Cat", 2)
    t3 = Task(103, "Brush Fur", datetime.now() + timedelta(hours=2), 10, frequency="Weekly")
    milo.add_task(t3)

    scheduler.add_pet(luna)
    scheduler.add_pet(milo)
    return scheduler
