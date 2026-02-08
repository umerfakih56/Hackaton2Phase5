# Feature Specification: Event-Driven Todo Chatbot

**Feature Branch**: `001-event-driven-todo`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Transform the Todo Chatbot into a distributed, event-driven, cloud-native system with recurring tasks, due dates & reminders, priorities, tags, search/filter/sort, Kafka integration, and Dapr components."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Priorities (Priority: P1)

As a user, I want to assign priority levels (High, Medium, Low) to my
tasks so I can focus on what matters most.

**Why this priority**: Priority assignment is the simplest, most
immediately valuable enhancement. It enriches every task record and is
a prerequisite for meaningful sorting and filtering. It can be delivered
as a standalone slice with zero dependency on eventing infrastructure.

**Independent Test**: Create a task, set its priority to High, verify
it appears with the correct priority badge and color coding in the task
list. Change priority to Low, confirm the update persists.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they do not select
   a priority, **Then** the task defaults to Medium priority.
2. **Given** a task exists with Medium priority, **When** the user
   changes its priority to High, **Then** the task list reflects the
   new priority with the corresponding color indicator (Red = High,
   Yellow = Medium, Green = Low).
3. **Given** a task list with mixed priorities, **When** the user sorts
   by priority, **Then** tasks appear in High → Medium → Low order.

---

### User Story 2 - Tags & Categories (Priority: P2)

As a user, I want to organize tasks with free-form tags so I can group
related work and filter my task list by topic.

**Why this priority**: Tags provide the organizational backbone for task
management. Once priorities exist, tags add the next layer of structure,
and both are consumed by the search/filter story.

**Independent Test**: Create a task, add tags "work" and "urgent",
verify both tags appear on the task. Create a second task with tag
"personal". Filter by "work" — only the first task appears.

**Acceptance Scenarios**:

1. **Given** a user is editing a task, **When** they type a tag name,
   **Then** the system suggests existing tags via autocomplete.
2. **Given** a task with tags "work" and "urgent", **When** the user
   filters by tag "work", **Then** only tasks containing the "work" tag
   are displayed.
3. **Given** a user removes all tags from a task, **When** they save,
   **Then** the task persists with an empty tag list.
4. **Given** multiple tasks use tag "work", **When** a user creates a
   new task and types "wo", **Then** "work" appears as an autocomplete
   suggestion.

---

### User Story 3 - Search, Filter & Sort (Priority: P3)

As a user, I want to search across my tasks by text, filter by status,
priority, tag, or due date range, and sort by various fields so I can
quickly find what I need.

**Why this priority**: Search/filter/sort is the discovery layer that
makes priorities (P1) and tags (P2) actionable at scale. It depends on
both being present for full value.

**Independent Test**: Create 10 tasks with varying priorities, tags,
statuses, and due dates. Search for a keyword — verify matching tasks
appear. Apply a priority filter — verify only matching priority tasks
show. Sort by due date — verify correct ordering.

**Acceptance Scenarios**:

1. **Given** tasks with titles "Buy groceries" and "Review budget",
   **When** the user searches "budget", **Then** only "Review budget"
   appears in results.
2. **Given** a mix of pending and completed tasks, **When** the user
   filters by status "pending", **Then** only pending tasks appear.
3. **Given** tasks with various due dates, **When** the user sorts by
   due date ascending, **Then** tasks with the earliest due dates
   appear first, and tasks without due dates appear last.
4. **Given** the user applies multiple filters (priority = High AND
   tag = "work"), **When** results load, **Then** only tasks matching
   all active filters are displayed.

---

### User Story 4 - Due Dates & Reminders (Priority: P4)

As a user, I want to set due dates on my tasks and receive reminders
before deadlines so I never miss important work.

**Why this priority**: Due dates add time-awareness to the task system
and introduce the first event-driven behavior (reminder scheduling).
This story bridges the gap between simple task management and the
event-driven architecture.

**Independent Test**: Create a task with a due date 1 hour from now,
set a reminder for 30 minutes before. Verify the reminder triggers at
the correct time (simulated notification in Phase V). Verify the due
date appears on the task card.

**Acceptance Scenarios**:

1. **Given** a user is editing a task, **When** they set a due date
   using the date/time picker, **Then** the due date is persisted and
   displayed on the task.
2. **Given** a task with due date and a "1 hour before" reminder
   configured, **When** the reminder time arrives, **Then** the system
   triggers a notification (simulated via console log or in-app
   notification in Phase V).
3. **Given** a task's due date has passed, **When** the user views the
   task list, **Then** the overdue task is visually highlighted
   (e.g., red text or badge).
4. **Given** a user removes the due date from a task, **When** they
   save, **Then** any associated reminder is cancelled.

---

### User Story 5 - Recurring Tasks (Priority: P5)

As a user, I want to create tasks that repeat automatically on a
schedule (daily, weekly, monthly, or custom) so I do not have to
manually re-create routine tasks.

**Why this priority**: Recurring tasks are the most advanced feature,
requiring event-driven processing (task completion triggers next
occurrence creation). It fully exercises the Kafka + Dapr eventing
pipeline and depends on the due date infrastructure from P4.

**Independent Test**: Create a task with daily recurrence, mark it
complete. Verify a new task is automatically created for the next day
with the same title, description, tags, and priority. Verify the
original task retains its completion history.

**Acceptance Scenarios**:

1. **Given** a user creates a task with recurrence set to "daily",
   **When** the user completes the task, **Then** the system
   automatically creates a new task for the next day inheriting the
   title, description, tags, and priority.
2. **Given** a task with weekly recurrence on Monday and Wednesday,
   **When** the Monday instance is completed, **Then** the next
   occurrence is created for Wednesday of the same week.
3. **Given** a recurring task with monthly recurrence on the 31st,
   **When** the current month has only 30 days, **Then** the next
   occurrence is scheduled for the last day of that month.
4. **Given** a user views a recurring task, **When** they check the
   task history, **Then** they can see all previous completions with
   timestamps.
5. **Given** a user edits a recurring task's recurrence pattern,
   **When** they save, **Then** only future occurrences follow the new
   pattern; past completions are unaffected.

---

### User Story 6 - Event-Driven Task Processing (Priority: P6)

As a system operator, I want all task mutations (create, update,
complete, delete) to publish events so that downstream services
(recurring task service, notification service) react automatically
without tight coupling.

**Why this priority**: This is the architectural foundation for the
event-driven system. It is sequenced after the business features
because it can be layered underneath them — the features work first
in a simple request-response mode, then events are wired in.

**Independent Test**: Create a task via the API, verify a "task.created"
event is published. Complete the task, verify a "task.completed" event
is published. Inspect event payloads for correct schema compliance.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the task is persisted,
   **Then** a standardized event with type "created", task data, user
   ID, and ISO 8601 timestamp is published to the task-events topic.
2. **Given** a user completes a recurring task, **When** the
   "completed" event is consumed by the Recurring Task Service,
   **Then** the next occurrence is created within 5 seconds.
3. **Given** a reminder event is published, **When** the Notification
   Service consumes it, **Then** the reminder is triggered at the
   scheduled time (within 1-minute tolerance).
4. **Given** the Notification Service is temporarily unavailable,
   **When** reminder events accumulate, **Then** they are processed
   in order once the service recovers (no events lost).

---

### User Story 7 - Dapr Infrastructure Abstraction (Priority: P7)

As a system operator, I want all infrastructure access (messaging,
state, secrets, scheduling) to go through Dapr building blocks so
the system is portable across cloud providers without code changes.

**Why this priority**: Dapr abstraction is the final architectural
layer. It replaces direct infrastructure calls with Dapr sidecar APIs.
It is lowest priority because the system must first work correctly
before abstracting infrastructure access.

**Independent Test**: Verify that no application code imports Kafka,
database, or secret manager client libraries directly. Verify all
Pub/Sub operations use Dapr HTTP endpoints. Swap a Dapr component
YAML (e.g., state store) and confirm the application functions
without code changes.

**Acceptance Scenarios**:

1. **Given** the application publishes a task event, **When** the
   publish call is inspected, **Then** it uses the Dapr Pub/Sub HTTP
   endpoint, not a direct Kafka client library.
2. **Given** a Dapr component YAML is changed from Kafka to a
   different Pub/Sub provider, **When** the application restarts,
   **Then** it continues to function without any code modifications.
3. **Given** the application reads a secret, **When** the call is
   inspected, **Then** it uses the Dapr Secrets API, not a direct
   secrets manager SDK.
4. **Given** a reminder needs scheduling, **When** the schedule
   request is made, **Then** it uses the Dapr Jobs API endpoint.

---

### Edge Cases

- What happens when a recurring task's recurrence pattern is set to
  "custom" but no custom rule is provided? System MUST reject the save
  with a validation error.
- How does the system handle a completed recurring task when the Kafka
  broker is temporarily unreachable? The completion is persisted locally
  and the event is retried with exponential backoff; the next occurrence
  is created once the event is successfully consumed.
- What happens when a user sets a reminder time in the past? System
  MUST either trigger the reminder immediately or reject the input with
  a warning, depending on how far in the past (< 5 minutes = trigger
  immediately, > 5 minutes = reject).
- What happens when a user searches with an empty query? System MUST
  return all tasks (unfiltered).
- What happens when filtering by a tag that no tasks use? System MUST
  return an empty result set with a clear "No tasks found" message.
- What happens when two users complete the same shared recurring task
  simultaneously? System MUST ensure exactly one next occurrence is
  created (idempotent event handling).
- What happens when the Dapr sidecar is unavailable? Service MUST
  return a 503 Service Unavailable with a meaningful error message
  and NOT fall back to direct infrastructure access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support three priority levels: High, Medium,
  Low, with Medium as the default for new tasks.
- **FR-002**: System MUST allow users to add, remove, and edit
  free-form text tags on any task, with no limit on tags per task.
- **FR-003**: System MUST provide tag autocomplete suggestions based
  on tags the current user has previously used.
- **FR-004**: System MUST support full-text search across task title
  and description fields.
- **FR-005**: System MUST support filtering by: status
  (pending/completed), priority (High/Medium/Low), tag(s), and due
  date range.
- **FR-006**: System MUST support sorting by: created date, due date,
  priority, and title (alphabetical), in both ascending and descending
  order.
- **FR-007**: System MUST allow users to set a due date (with time)
  on any task via a date/time picker.
- **FR-008**: System MUST allow users to configure reminder timing
  relative to due date (e.g., 15 minutes, 1 hour, 1 day, 1 week
  before).
- **FR-009**: System MUST trigger reminders at the configured time
  using scheduled job infrastructure (not polling).
- **FR-010**: Reminders in Phase V MUST be simulated via in-app
  notification or console log output.
- **FR-011**: System MUST support recurrence patterns: daily, weekly
  (specific days of week), monthly (specific day of month), and
  custom interval (every N days).
- **FR-012**: When a recurring task is completed, system MUST
  automatically create the next occurrence inheriting title,
  description, tags, and priority.
- **FR-013**: System MUST retain the completion history for recurring
  tasks (list of completion timestamps).
- **FR-014**: System MUST publish a standardized event for every task
  mutation (create, update, complete, delete) to the task-events topic.
- **FR-015**: Event payloads MUST include: event_type, task_id,
  task_data, user_id, and ISO 8601 timestamp.
- **FR-016**: System MUST publish reminder events to the reminders
  topic when a reminder is created or updated.
- **FR-017**: All inter-service messaging MUST use the platform's
  Pub/Sub abstraction layer (no direct message broker client libraries).
- **FR-018**: All secret access MUST go through the platform's secrets
  abstraction (no hardcoded credentials or direct SDK calls).
- **FR-019**: Event handlers MUST be idempotent — processing the same
  event multiple times MUST NOT create duplicate data or side effects.
- **FR-020**: System MUST visually indicate overdue tasks (past due
  date) with distinct styling in the task list.

### Key Entities

- **Task**: Represents a unit of work. Key attributes: title,
  description, status (pending/completed), priority (High/Medium/Low),
  due date, recurrence pattern, tags, created timestamp, updated
  timestamp, completed timestamp, user ownership.
- **Tag**: A free-form text label attached to tasks. Many-to-many
  relationship with Task. Unique per user namespace.
- **Recurrence Rule**: Defines the repeat pattern for a task. Attributes:
  type (daily/weekly/monthly/custom), day-of-week selections (for weekly),
  day-of-month (for monthly), interval (for custom), parent task reference.
- **Reminder**: A scheduled notification tied to a task's due date.
  Attributes: task reference, remind-at timestamp, status
  (pending/triggered/cancelled), notification channel.
- **Task Event**: An immutable record of a task mutation. Attributes:
  event type, task ID, full task data snapshot, user ID, timestamp,
  correlation ID.
- **Completion Record**: A historical entry for recurring task completions.
  Attributes: task reference, completion timestamp, completed-by user.

### Assumptions

- A single user mode is assumed for Phase V; multi-user features
  (shared tasks, team collaboration) are out of scope.
- Email and push notifications are simulated (console log / in-app
  toast) in Phase V. Real notification channels are a future concern.
- The AI chatbot interface (OpenAI Agents SDK) is the primary
  interaction surface, with a supporting web UI for visual task
  management.
- Task data retention follows standard practice — no automatic
  deletion of completed tasks unless the user explicitly deletes them.
- The "custom" recurrence pattern supports only fixed-interval
  repetition (every N days), not complex rules like "every second
  Tuesday" (out of scope for Phase V).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with priority, tags, and due
  date in under 30 seconds via the chatbot interface.
- **SC-002**: Full-text search returns matching results within 2
  seconds for a task list of up to 10,000 tasks.
- **SC-003**: Filtering and sorting operations complete within 1
  second for up to 10,000 tasks.
- **SC-004**: When a recurring task is completed, the next occurrence
  appears within 5 seconds.
- **SC-005**: Reminders trigger within 1 minute of the scheduled
  reminder time.
- **SC-006**: The system handles 100 concurrent users performing task
  operations without degradation.
- **SC-007**: Zero direct infrastructure client library imports exist
  in application code — all infrastructure access goes through the
  abstraction layer.
- **SC-008**: Swapping an infrastructure component configuration
  requires zero application code changes.
- **SC-009**: No task events are lost during temporary downstream
  service outages of up to 5 minutes.
- **SC-010**: 95% of users can successfully create, tag, prioritize,
  and find tasks on their first attempt without documentation.
