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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
