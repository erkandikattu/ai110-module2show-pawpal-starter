# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Three core actions the user should be able to perform are adding a pet, scheduling pet tasks (e.g. walk, feeding, grooming, etc.), and see viable schedules based on constraints.
- Briefly describe your initial UML design.
I chose classes for the 4 main components of Owner, Pet, Task, Scheduler. I also chose additional helper classes called DailyPlan and PlannedItem to help create schedules from tasks. Owner, Pet, and Task all work in the traditional sense.
- What classes did you include, and what responsibilities did you assign to each?
I included the 4 main classes and 2 helper classes called PlannedItem and DailyPlan. The PlannedItem class represents tasks with start and end times. The DailyPlan class represents the tasks planned for a specific date. The scheduler then uses DailyPlan and PlannedItem to generate schedules. Owner has preferences, pets, and availability. Pet has pet attributes and tasks. Task has duration, priority, and constraints. 

**b. Design changes**

- Did your design change during implementation? Yes, some logic errors and missing relationships were identified.
- If yes, describe at least one change and why you made it.
Previously, an owner could have many pets, but scheduling tasks was only available for a single pet at a time. This is a logic error that was fixed by allowing the scheduler to schedule tasks for multiple pets. Also, planned tasks did not identify which pet the task is assigned to. This logic error was fixed by idnetfying which pet a task is assigned to as a parameter.
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
