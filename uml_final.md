# PawPal+ Final UML Class Diagram

```mermaid
classDiagram
    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +String frequency
        +bool completed
        +String scheduled_time
        +date due_date
        +mark_complete() void
        +is_high_priority() bool
        +next_occurrence() Task
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~Task~ tasks
        +add_task(task: Task) void
        +remove_task(title: String) void
        +get_tasks() List~Task~
        +complete_task(title: String) Task
        +get_profile() String
    }

    class Owner {
        +String name
        +int available_minutes
        +String preferences
        +List~Pet~ pets
        +add_pet(pet: Pet) void
        +remove_pet(name: String) void
        +get_all_tasks() List~Task~
        +get_available_time() int
        +update_preferences(pref: String) void
    }

    class Scheduler {
        +Owner owner
        +List~Task~ scheduled_tasks
        +List~Task~ skipped_tasks
        +build_plan() void
        +filter_scheduled(pet_name, completed, category) List~Task~
        +sort_by_time() List~Task~
        +detect_conflicts() List~String~
        +get_skipped_tasks() List~Task~
        +explain_plan() String
        +display_plan() String
        -_to_minutes(time_str: String) int
    }

    Owner "1" --> "many" Pet : manages
    Pet "1" --> "many" Task : owns
    Scheduler "1" --> "1" Owner : reads from
    Scheduler ..> Task : schedules / skips
```

## What changed from the initial design

| Class | Change | Why |
|---|---|---|
| `Task` | Added `frequency`, `scheduled_time`, `due_date`, `next_occurrence()` | Needed for recurring task logic and time-based sorting/conflict detection |
| `Pet` | Removed `owner` back-reference; added `tasks` list and task management methods; added `complete_task()` | Owner → Pet is sufficient; Pet needed to own its tasks directly to support recurrence |
| `Owner` | Added `pets` list and aggregation method `get_all_tasks()` | Owner manages multiple pets; Scheduler retrieves all tasks through Owner |
| `Scheduler` | Removed single `pet` and `tasks` references; added `filter_scheduled`, `sort_by_time`, `detect_conflicts` | Scheduler now works across all pets via Owner; algorithmic methods added in Phase 3 |

## How to export as PNG

Open [https://mermaid.live](https://mermaid.live), paste the diagram code above, and use **Export → PNG**.
Alternatively, use the VS Code **Markdown Preview Mermaid Support** extension to render and screenshot.
