---
id: 002
title: Create Event-Driven Todo Spec
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 001-event-driven-todo
branch: 001-event-driven-todo
user: user
command: /sp.specify
labels: ["spec", "event-driven", "todo", "kafka", "dapr"]
links:
  spec: specs/001-event-driven-todo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-event-driven-todo/spec.md
  - specs/001-event-driven-todo/checklists/requirements.md
tests:
---

## Prompt

Feature Requirements
A. Advanced Level Features
1. Recurring Tasks

User Story: As a user, I want to create tasks that repeat automatically (daily, weekly, monthly)
Acceptance Criteria:

User can set recurrence pattern: daily, weekly (specific days), monthly, custom
When recurring task is completed, system auto-creates next occurrence
Next occurrence inherits title, description, tags, and priority
Event-driven: Task completion publishes to Kafka task-events topic
Recurring Task Service consumes event and creates next task
Original task retains history of completions



2. Due Dates & Reminders

User Story: As a user, I want to set due dates and receive reminders before deadlines
Acceptance Criteria:

User can set due date with time picker
User can configure reminder timing (e.g., 1 hour before, 1 day before)
Reminder creation publishes to Kafka reminders topic
Notification Service consumes and triggers alerts at scheduled time
Reminders sent via email/push notification (simulated in Phase V)
Dapr Jobs API used for exact-time reminder triggers (not cron polling)



B. Intermediate Level Features
3. Priorities

User Story: As a user, I want to assign priority levels to tasks
Acceptance Criteria:

Three priority levels: High, Medium, Low
Default priority: Medium
Tasks can be filtered and sorted by priority
Priority visible in task list UI with color coding



4. Tags/Categories

User Story: As a user, I want to organize tasks with tags
Acceptance Criteria:

User can add multiple tags to a task
Tags are free-form text
Autocomplete suggests existing tags
Tasks can be filtered by tag(s)



5. Search, Filter, Sort

User Story: As a user, I want to find tasks quickly
Acceptance Criteria:

Search: Full-text search across title and description
Filter: By status (pending/completed), priority, tag, due date range
Sort: By created date, due date, priority, title (alphabetical)



C. Event-Driven Architecture
6. Kafka Integration

Event Schema Standardization with task events and reminder events.
Kafka Topics: task-events, reminders, task-updates.
Producers: Chat API / MCP Tools.
Consumers: Recurring Task Service, Notification Service, Audit Service.

7. Dapr Components

Pub/Sub (kafka-pubsub), State Management (statestore), Jobs API (dapr-jobs), Secrets (kubernetes-secrets).

## Response snapshot

Created feature specification for the Event-Driven Todo Chatbot on branch `001-event-driven-todo`. The spec contains 7 prioritized user stories (P1: Priorities, P2: Tags, P3: Search/Filter/Sort, P4: Due Dates & Reminders, P5: Recurring Tasks, P6: Event-Driven Processing, P7: Dapr Abstraction), 20 functional requirements, 6 key entities, 7 edge cases, 10 measurable success criteria, and 5 documented assumptions. All quality validation checks passed (no NEEDS CLARIFICATION markers, no implementation details, all Given/When/Then scenarios, all placeholders resolved). Spec is ready for `/sp.clarify` or `/sp.plan`.

## Outcome

- ✅ Impact: Complete feature specification created, validated, and ready for planning
- 🧪 Tests: N/A (specification document)
- 📁 Files: specs/001-event-driven-todo/spec.md, specs/001-event-driven-todo/checklists/requirements.md
- 🔁 Next prompts: /sp.clarify or /sp.plan
- 🧠 Reflection: User provided very detailed requirements including event schemas and Dapr component details. Reordered priorities to build incrementally (simple features first, architecture last). No clarifications needed due to comprehensive input.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script failed on long feature description (positional param parsing issue); recovered manually
- Graders run and results (PASS/FAIL): Spec quality validation — PASS (5/5 checks)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
