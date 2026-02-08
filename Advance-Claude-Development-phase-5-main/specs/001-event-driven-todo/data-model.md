# Data Model: Event-Driven Todo Chatbot

**Feature Branch**: `001-event-driven-todo`
**Date**: 2026-02-07
**Source**: spec.md (Key Entities), user architecture input

## Entity Relationship Overview

```text
User 1──* Task *──* Tag
              │
              ├── 0..1 RecurrenceRule
              ├── 0..1 Reminder
              └── 0..* CompletionRecord

Task 1──* TaskEvent (immutable audit log)
```

## Entities

### 1. User

Represents an authenticated user of the system.

| Field          | Type         | Constraints                     |
|----------------|--------------|---------------------------------|
| id             | UUID         | Primary key                     |
| email          | String(255)  | Unique, NOT NULL                |
| name           | String(255)  | NOT NULL                        |
| created_at     | Timestamp TZ | NOT NULL, default NOW()         |
| updated_at     | Timestamp TZ | NOT NULL, auto-updated          |

**Notes**: Managed by Better Auth. Minimal fields stored in application
database; auth tokens managed externally.

---

### 2. Task

The core entity representing a unit of work.

| Field               | Type          | Constraints                          |
|---------------------|---------------|--------------------------------------|
| id                  | Serial INT    | Primary key, auto-increment          |
| user_id             | UUID          | FK → User.id, NOT NULL, indexed      |
| title               | String(500)   | NOT NULL, min length 1               |
| description         | Text          | Nullable, default empty              |
| status              | Enum          | "pending" / "completed", NOT NULL    |
| priority            | Enum          | "high" / "medium" / "low", NOT NULL  |
| due_date            | Timestamp TZ  | Nullable                             |
| is_recurring        | Boolean       | NOT NULL, default false              |
| recurrence_pattern  | JSONB         | Nullable (see RecurrenceRule schema) |
| reminder_offset     | String(50)    | Nullable (e.g., "1h", "1d", "15m")  |
| created_at          | Timestamp TZ  | NOT NULL, default NOW()              |
| updated_at          | Timestamp TZ  | NOT NULL, auto-updated               |
| completed_at        | Timestamp TZ  | Nullable                             |
| search_vector       | tsvector      | Generated from title + description   |

**Default values**:
- `status`: "pending"
- `priority`: "medium"
- `is_recurring`: false

**Indexes**:
- `idx_task_user_id` on user_id
- `idx_task_status` on status
- `idx_task_priority` on priority
- `idx_task_due_date` on due_date
- `idx_task_search` GIN index on search_vector
- `idx_task_created_at` on created_at

**Validation rules**:
- `title` MUST NOT be empty or whitespace-only.
- `priority` MUST be one of: "high", "medium", "low".
- `status` MUST be one of: "pending", "completed".
- If `is_recurring` is true, `recurrence_pattern` MUST NOT be null.
- `reminder_offset` requires `due_date` to be set.
- `due_date` MUST be in the future when first set (with 5-minute
  grace window per edge case spec).

---

### 3. Tag

Free-form text labels for organizing tasks. Stored as a normalized
junction table for efficient querying and autocomplete.

| Field      | Type         | Constraints                          |
|------------|--------------|--------------------------------------|
| id         | Serial INT   | Primary key                          |
| name       | String(100)  | NOT NULL, min length 1               |
| user_id    | UUID         | FK → User.id, NOT NULL               |
| created_at | Timestamp TZ | NOT NULL, default NOW()              |

**Unique constraint**: (name, user_id) — tags are unique per user.

**Index**: `idx_tag_user_name` on (user_id, name) for autocomplete.

---

### 4. TaskTag (Junction Table)

Many-to-many relationship between Task and Tag.

| Field   | Type       | Constraints                      |
|---------|------------|----------------------------------|
| task_id | INT        | FK → Task.id, NOT NULL           |
| tag_id  | INT        | FK → Tag.id, NOT NULL            |

**Primary key**: (task_id, tag_id)

**Cascade**: Deleting a Task removes its TaskTag rows.

---

### 5. RecurrenceRule (embedded as JSONB in Task)

Stored as a JSONB column `recurrence_pattern` on the Task entity.

```json
{
  "type": "daily" | "weekly" | "monthly" | "custom",
  "days_of_week": [0, 1, 2, 3, 4, 5, 6],
  "day_of_month": 15,
  "interval_days": 3,
  "parent_task_id": null
}
```

| Field          | Type       | Used When         | Constraints            |
|----------------|------------|-------------------|------------------------|
| type           | String     | Always            | Required               |
| days_of_week   | Int array  | type = "weekly"   | 0=Mon ... 6=Sun        |
| day_of_month   | Int        | type = "monthly"  | 1-31                   |
| interval_days  | Int        | type = "custom"   | Min 1                  |
| parent_task_id | Int/null   | Child occurrences | FK → Task.id           |

**Validation rules**:
- If `type` = "weekly", `days_of_week` MUST have at least one entry.
- If `type` = "monthly", `day_of_month` MUST be 1–31.
- If `type` = "custom", `interval_days` MUST be >= 1.
- `parent_task_id` is set on auto-created child occurrences to link
  back to the original recurring task.

---

### 6. Reminder

A scheduled notification tied to a task's due date.

| Field       | Type          | Constraints                          |
|-------------|---------------|--------------------------------------|
| id          | Serial INT    | Primary key                          |
| task_id     | INT           | FK → Task.id, NOT NULL, unique       |
| user_id     | UUID          | FK → User.id, NOT NULL               |
| remind_at   | Timestamp TZ  | NOT NULL, computed from due_date     |
| status      | Enum          | "pending" / "triggered" / "cancelled"|
| job_name    | String(255)   | Dapr Jobs API job identifier         |
| created_at  | Timestamp TZ  | NOT NULL, default NOW()              |
| updated_at  | Timestamp TZ  | NOT NULL, auto-updated               |

**Default**: `status` = "pending"

**Validation rules**:
- `remind_at` MUST be before the task's `due_date`.
- One reminder per task (unique constraint on task_id).
- When task's due_date is removed, reminder status → "cancelled".
- `job_name` format: `reminder-task-{task_id}`

---

### 7. CompletionRecord

Historical entry for recurring task completions.

| Field          | Type          | Constraints                      |
|----------------|---------------|----------------------------------|
| id             | Serial INT    | Primary key                      |
| task_id        | INT           | FK → Task.id, NOT NULL, indexed  |
| completed_at   | Timestamp TZ  | NOT NULL, default NOW()          |
| completed_by   | UUID          | FK → User.id, NOT NULL           |

**Index**: `idx_completion_task_id` on task_id for history queries.

---

### 8. Conversation

Chat session for the AI chatbot interface.

| Field      | Type          | Constraints                      |
|------------|---------------|----------------------------------|
| id         | UUID          | Primary key                      |
| user_id    | UUID          | FK → User.id, NOT NULL, indexed  |
| title      | String(500)   | Nullable                         |
| created_at | Timestamp TZ  | NOT NULL, default NOW()          |
| updated_at | Timestamp TZ  | NOT NULL, auto-updated           |

---

### 9. Message

Individual messages within a conversation.

| Field           | Type          | Constraints                      |
|-----------------|---------------|----------------------------------|
| id              | UUID          | Primary key                      |
| conversation_id | UUID          | FK → Conversation.id, NOT NULL   |
| role            | Enum          | "user" / "assistant" / "system"  |
| content         | Text          | NOT NULL                         |
| created_at      | Timestamp TZ  | NOT NULL, default NOW()          |

**Index**: `idx_message_conversation` on (conversation_id, created_at).

---

## Event Schemas

### TaskEvent (Kafka topic: task-events)

```json
{
  "event_type": "created" | "updated" | "completed" | "deleted",
  "task_id": 123,
  "task_data": {
    "id": 123,
    "title": "Buy groceries",
    "description": "Weekly grocery shopping",
    "status": "completed",
    "priority": "medium",
    "tags": ["shopping", "weekly"],
    "due_date": "2026-02-08T10:00:00Z",
    "is_recurring": true,
    "recurrence_pattern": {"type": "weekly", "days_of_week": [5]}
  },
  "user_id": "uuid-string",
  "timestamp": "2026-02-07T14:30:00Z",
  "correlation_id": "uuid-string"
}
```

### ReminderEvent (Kafka topic: reminders)

```json
{
  "task_id": 123,
  "title": "Buy groceries",
  "due_at": "2026-02-08T10:00:00Z",
  "remind_at": "2026-02-08T09:00:00Z",
  "user_id": "uuid-string",
  "correlation_id": "uuid-string"
}
```

## State Transitions

### Task Status

```text
pending ──[complete]-→ completed
pending ──[delete]──-→ (deleted/removed)
completed ──[reopen]-→ pending
```

### Reminder Status

```text
pending ──[trigger time arrives]-→ triggered
pending ──[due_date removed]────-→ cancelled
pending ──[task deleted]─────────→ cancelled
```

## Migration Strategy

All schema changes MUST use versioned migration scripts (Alembic).
Each migration MUST be forward-only with a documented rollback
procedure. Migrations MUST be idempotent where possible.
