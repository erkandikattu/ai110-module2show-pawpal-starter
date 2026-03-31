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
My scheduler considers time and preferences for initial task validation. Then, it considers priority, status, and due-time for ordering valid tasks.
- How did you decide which constraints mattered most?
I prioritized the constraints based on impact. I first prioritized constraints like time and preferences that helps to eliminate invalid tasks. Then, I prioritized constraints that help filter efficiently like status and due-time. Overall, I prioritized constraints for eliminating invalid tasks and filtering tasks effectively for schedule generation.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
My scheduler uses a greedy approach and schedules high ranked tasks by due-time instead of finding the best overall schedule.
- Why is that tradeoff reasonable for this scenario?
It is reasonable because users and pet owners need fast daily plans that are simple. The perfect plan taks time to create and might be more complex.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI tools like Copilot to help design the UML diagram, plan feature/logic implementation, create a variety of unit tests, and more. I also used it for debugging as well as refactoring functions.
I also used different chat sessions to focus on different steps of the app (e.g. UML design, generating tests, modifying functions).
- What kinds of prompts or questions were most helpful?
Using plan mode and asking questions about how to implement a feature was very helpful. Instead of just asking an agent to implement the feature, using plan/ask to brainstorm approaches to the implementation was more helpful and often led to better results.
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
Copilot initially gave me a UML diagram that did not support certain desired behaviors of the app. The main problem was interaction and relationships between classes (e.g. Tasks being assigned to multiple or individual pets). 
- How did you evaluate or verify what the AI suggested?
I read through the UML diagram and used ask mode to ask why this logic was not implemented. Then, I used plan mode to plan how to modify the existing UML diagram to incorporate inter-class relationships. Then, agent mode implemented the suggested fixes.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested core behaviors like adding pets, generating schedules, and assigning tasks. I also tested more advanced behaviors like sorting tasks based on due-time, generating schedules efficiently, and filtering tasks based on priority, status, etc. I also tested for task conflict.
- Why were these tests important?
These tests were important to ensure that both happy cases and edge cases were considered when implementing the app. These tests give more confidence that the app can handle all situations and run as expected.
**b. Confidence**

- How confident are you that your scheduler works correctly?
I am very confident that the scheduler works correctly. After reviewing method implementation and unit tests in the app, I believe that most edge and happy cases have been addressed. 
- What edge cases would you test next if you had more time?
I would test edge cases like having a pet assigned to multiple owners (e.g. a pet belonging to a family).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most satisfied with the end-to-end aspect of the project. I went from designing the UML diagram all the way to a complete implementation of the classes, methods, and running the app properly.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would try to refactor more methods in pawpal_system.py as I believe that they could be simplified more. I would also add additional functionality for schedules such as allowing the user to choose between the best overall schedule and the simple/"greedy" schedule.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned more about using UML diagrams in the introductory stages of projects to design and plan before implementation. Designing the UML diagrams early allows both me and the AI assistant to address any issues and design flaws early on. Afterwards, the implementation is straightforward and more clear.
