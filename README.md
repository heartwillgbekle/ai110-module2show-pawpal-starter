# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduling logic in `pawpal_system.py` goes beyond a simple list of tasks. Four algorithms make it more intelligent:

**Frequency-aware sorting** — Tasks are sorted before scheduling using a three-key sort: frequency first (`daily` → `weekly` → `as-needed`), then priority (`high` → `low`), then duration (shortest first as a tiebreaker). This ensures a dog's daily medication is always considered before a weekly grooming session, regardless of how tasks were added.

**Time-based sorting** — `Scheduler.sort_by_time()` orders the scheduled plan by each task's preferred start time (`HH:MM`). Because the strings are zero-padded, lexicographic order equals chronological order — no date parsing required. Tasks without a start time sort to the end.

**Filtering** — `Scheduler.filter_scheduled()` accepts any combination of `pet_name`, `completed`, and `category` to return a focused subset of the scheduled plan. Filters can be stacked: e.g., all incomplete feed tasks for a specific pet.

**Conflict detection** — `Scheduler.detect_conflicts()` runs three checks and returns plain-language warnings without crashing the program:
- Duplicate task titles (among incomplete tasks) for the same pet
- Daily-task total exceeding the owner's available time budget
- Overlapping time windows between any two scheduled tasks, using interval arithmetic (`start_A < end_B and start_B < end_A`)

**Recurring tasks** — Calling `Pet.complete_task(title)` marks a task done and automatically appends the next occurrence to the pet's task list. Daily tasks recur tomorrow (`timedelta(days=1)`), weekly tasks recur in seven days (`timedelta(days=7)`), and as-needed tasks do not recur.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
