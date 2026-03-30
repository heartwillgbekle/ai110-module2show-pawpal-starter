from pawpal_system import Task, Pet


def test_mark_complete_changes_task_status():
    task = Task(
        title="Morning walk",
        duration_minutes=20,
        priority="high",
        category="walk",
        frequency="daily",
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", 10, "high", "feed", "daily"))
    assert len(pet.get_tasks()) == 1

    pet.add_task(Task("Grooming", 30, "medium", "grooming", "weekly"))
    assert len(pet.get_tasks()) == 2
