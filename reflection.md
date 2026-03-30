# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Three core user actions:**

1. **Enter owner and pet info** — A user enters basic profile details such as the owner's name, the pet's name and type, and how much time is available each day for care. This context gives the scheduler the constraints it needs to build a realistic plan.

2. **Add and edit care tasks** — A user creates tasks (e.g., morning walk, feeding, medication, grooming) and assigns each a duration and priority level. Tasks can be updated or removed as the pet's needs change from day to day.

3. **Generate and view a daily schedule** — A user requests a daily plan and the app arranges tasks within the available time window based on priority and constraints, then displays the ordered schedule along with an explanation of why each task was included or left out.

The initial design uses four classes. `Owner` holds the pet owner's name, daily time budget, and care preferences — it is the source of the constraint that the scheduler works within. `Pet` holds profile info (name, species, age) that describes who is being cared for. `Task` represents a single care activity and carries the title, duration, priority, category, and completion status needed to make scheduling decisions. `Scheduler` is the core logic class: it holds the owner, the pet, and the full task list, then produces two output lists — scheduled tasks that fit within the time budget and skipped tasks that did not — along with a plain-language explanation of the plan.

**b. Design changes**

After reviewing the skeleton, three changes were made. First, `Pet.owner` was removed as an attribute. The original UML gave `Pet` a back-reference to `Owner`, but `Scheduler` already holds `Owner` directly, making the link on `Pet` redundant and potentially confusing. Second, a `PRIORITY_LEVELS` constant (`{"low": 1, "medium": 2, "high": 3}`) was added at the module level. Because `priority` is stored as a plain string, `build_plan()` needs a consistent numeric mapping to sort and compare tasks — without it, string comparisons like `"high" > "low"` would be unreliable. Third, the unused `field` import from `dataclasses` was removed to keep the module clean. One potential bottleneck was also noted but left for the logic phase: when two tasks share the same priority level there is currently no tiebreaker, so `build_plan()` will need a secondary sort key (such as duration or category) to produce a deterministic schedule.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints. First and most important is the time budget: `owner.available_minutes` sets a hard ceiling — no task is ever scheduled if it would cause the total to exceed this number. Second is frequency: daily tasks are always considered before weekly or as-needed ones because they recur every day and skipping them has immediate consequences for the pet. Third is priority within a frequency group: a high-priority daily task (medication) ranks above a medium-priority daily task (enrichment). Duration acts as a final tiebreaker — when everything else is equal, shorter tasks go first, which maximises the number of activities that fit in the budget.

Time budget was chosen as the hardest constraint because it is non-negotiable: the owner only has a finite amount of time regardless of how important a task is. Frequency came second because a daily task that is skipped today is already overdue; a weekly task that is skipped today still has six more days of window.

**b. Tradeoffs**

The scheduler uses a greedy algorithm: it sorts tasks by frequency, then priority, then duration, and fills the time budget from the top of that list until no more tasks fit. This is simple and fast but does not guarantee the optimal set of tasks. For example, the scheduler might pick three short high-priority tasks that together consume 55 minutes, leaving only 5 minutes — not enough for a 10-minute medium-priority task that would have fit if one of the shorter tasks had been swapped out. A true optimal solution would use dynamic programming (the 0/1 knapsack algorithm), which evaluates all possible combinations to find the highest-value set that fits within the budget.

The greedy approach is a reasonable tradeoff here because a pet care app typically has a small number of tasks (under 20), so the difference between greedy and optimal is unlikely to matter in practice. More importantly, the greedy approach is transparent — a pet owner can read the priority order and predict exactly which tasks will be chosen, which builds trust in the app. An optimal knapsack solution would be harder to explain and harder for a non-technical user to reason about.

---

## 3. AI Collaboration

**a. How I used AI**

AI tools were used in four distinct ways across the project. During the design phase, I used them for brainstorming — asking for a list of classes and responsibilities, which gave me a starting point I could react to and refine rather than starting from a blank page. During implementation, I used them to draft method bodies (particularly the sorting lambda and the `timedelta` recurrence logic), which saved time on syntax and let me focus on the logic decisions. During the algorithmic phase, I used them to suggest improvements to existing code — the refactor from a nested `enumerate` loop to `itertools.combinations` came from this kind of prompt. During testing, I used them to generate an initial list of edge cases, then evaluated each one against my actual implementation to decide what was worth writing.

The most effective prompts were specific and grounded in the code. Questions like "given this sort key, what happens when two tasks have the same priority and duration?" produced sharper answers than broad questions like "how should I sort tasks?" Asking for comparisons ("what is the difference between greedy and knapsack for this use case?") was also more useful than asking for a single recommendation.

**b. Judgment and verification**

One suggestion I rejected was replacing `build_plan()`'s greedy algorithm with a dynamic programming knapsack solution. The AI framed this as a straightforward improvement — more optimal, same interface. I evaluated it by thinking through the user-facing consequences: a knapsack solution would sometimes produce a schedule that looked arbitrary to a pet owner (a medium-priority task selected over a high-priority one because the combination had higher total value), and it would be much harder to write a plain-language explanation for. I verified the greedy approach was sufficient by running the 21-test suite and confirming that every scenario produced a result the owner could predict and trust, then documented the tradeoff explicitly in section 2b. The AI suggestion was technically correct but wrong for this product.

I also modified the suggestion to use `t.scheduled_time or "99:99"` in the sort key. The AI proposed this as a simplification of the longer ternary, which it is, but I first verified that `None or "99:99"` evaluates to `"99:99"` in Python (it does, because `None` is falsy) before accepting it. I would not have accepted a shorthand I couldn't reason through.

---

## 4. Testing and Verification

**a. What I tested**

The 21-test suite covers six areas: basic `Task` and `Pet` operations, five `build_plan` happy-path scenarios, three empty-state edge cases, five recurring task scenarios, four conflict detection cases, and two sorting cases. The most important tests were the edge cases — specifically "pet with no tasks," "owner with no pets," and "all tasks already completed." These are the states most likely to crash an app that only gets tested on the happy path, and catching them early prevented silent failures in the Streamlit UI where an empty schedule would simply show nothing rather than throw an error.

The conflict detection tests were also critical because the interval arithmetic (`start_A < end_B and start_B < end_A`) has a non-obvious boundary condition: tasks that touch exactly end-to-start are not a conflict. Having a test that explicitly verifies this boundary (`test_detect_conflicts_no_overlap`) prevents a future change from accidentally tightening the comparison to `<=` and producing false positives.

**b. Confidence**

I am confident the scheduler's core logic is correct for the scenarios it was designed to handle. The greedy algorithm, recurrence chain, time-overlap detection, and sort order all have direct test coverage, and the edge cases around empty states are verified. My confidence drops at the integration layer: the Streamlit UI wiring — particularly the interaction between `st.session_state` persistence and the filter controls — was tested manually and could break in ways the unit tests would not catch. If I had more time, I would test two additional edge cases: a task whose `scheduled_time` is malformed (e.g., `"7:5"` instead of `"07:05"`) to verify `_to_minutes` handles it gracefully, and a recurring task that is completed multiple times in the same session to ensure the task list does not grow unboundedly.

---

## 5. Reflection

**a. What went well**

The thing I am most satisfied with is the recurrence chain. `Pet.complete_task()` calling `Task.next_occurrence()` and appending the result is a small, clean design that does one thing: when a task is done, the next instance appears automatically with the correct due date. It required no changes to any other class, and it is tested end-to-end in two lines of test code. That kind of self-contained, composable behavior is what good object-oriented design is supposed to produce, and getting it right on the first attempt — rather than through refactoring — was satisfying.

**b. What I would improve**

If I had another iteration, I would redesign the conflict detection to be prescriptive rather than just descriptive. Currently, `detect_conflicts()` returns a list of warning strings and leaves the resolution entirely to the user. A better version would suggest a fix alongside each warning — for example, "Morning walk (07:00, 20 min) overlaps with Feeding (07:10, 10 min). Consider moving Feeding to 07:20." This would make the app genuinely useful rather than just informative. I would also add a `time_block` concept to the scheduler — a contiguous window the owner specifies (e.g., 07:00–09:00) — so the plan could sequence tasks within a real time frame rather than just sorting by preferred start times.

**c. Key takeaway**

The most important thing I learned is that working with AI requires staying in the role of lead architect at every step. AI tools are fast at producing plausible-looking code and compelling-sounding explanations, which makes it easy to accept suggestions without fully thinking them through. The moments that mattered most on this project were the moments I slowed down and asked "does this fit the system I am building, or does it just solve the narrow question I asked?" The knapsack example is the clearest case: the AI was right that dynamic programming produces a more optimal schedule, but I was right that a more optimal schedule is not the same as a better product for this user. Knowing the difference between those two things — and being willing to reject a technically correct suggestion — is what it means to be the architect rather than just the typist.

---
