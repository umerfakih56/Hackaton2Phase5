# Backend API Contract

**Service**: Backend API (FastAPI + MCP Tools)
**Base Path**: `/api`
**Auth**: JWT Bearer token required on all endpoints

## Chat Endpoint

### POST /api/{user_id}/chat

Process a user chat message through the AI agent.

**Request**:
```json
{
  "message": "Add a high priority task to buy groceries by Friday",
  "conversation_id": "uuid-or-null"
}
```

**Response** (200):
```json
{
  "response": "I've created a high priority task 'Buy groceries' due Friday.",
  "conversation_id": "uuid",
  "actions_taken": [
    {
      "tool": "add_task",
      "result": {"task_id": 123, "title": "Buy groceries"}
    }
  ]
}
```

**Errors**: 401 Unauthorized, 422 Validation Error, 503 Service Unavailable

---

## Task CRUD Endpoints

### GET /api/tasks

List tasks with filtering, sorting, and search.

**Query Parameters**:

| Parameter  | Type     | Required | Description                        |
|------------|----------|----------|------------------------------------|
| q          | string   | No       | Full-text search query             |
| status     | string   | No       | "pending" or "completed"           |
| priority   | string   | No       | "high", "medium", or "low"         |
| tags       | string[] | No       | Filter by tag names (AND logic)    |
| due_from   | datetime | No       | Due date range start (ISO 8601)    |
| due_to     | datetime | No       | Due date range end (ISO 8601)      |
| sort_by    | string   | No       | "created_at", "due_date", "priority", "title" |
| sort_order | string   | No       | "asc" or "desc" (default: "desc")  |
| page       | int      | No       | Page number (default: 1)           |
| page_size  | int      | No       | Items per page (default: 20, max: 100) |

**Response** (200):
```json
{
  "tasks": [
    {
      "id": 123,
      "title": "Buy groceries",
      "description": "Weekly grocery shopping",
      "status": "pending",
      "priority": "high",
      "tags": ["shopping", "weekly"],
      "due_date": "2026-02-08T10:00:00Z",
      "is_recurring": true,
      "recurrence_pattern": {"type": "weekly", "days_of_week": [5]},
      "reminder_offset": "1h",
      "created_at": "2026-02-07T14:00:00Z",
      "updated_at": "2026-02-07T14:00:00Z",
      "completed_at": null
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20
}
```

---

### POST /api/tasks

Create a new task. Publishes "created" event to task-events topic.

**Request**:
```json
{
  "title": "Buy groceries",
  "description": "Weekly grocery shopping",
  "priority": "high",
  "tags": ["shopping", "weekly"],
  "due_date": "2026-02-08T10:00:00Z",
  "reminder_offset": "1h",
  "is_recurring": true,
  "recurrence_pattern": {"type": "weekly", "days_of_week": [5]}
}
```

**Response** (201):
```json
{
  "id": 123,
  "title": "Buy groceries",
  "status": "pending",
  "priority": "high",
  "tags": ["shopping", "weekly"],
  "due_date": "2026-02-08T10:00:00Z",
  "is_recurring": true,
  "recurrence_pattern": {"type": "weekly", "days_of_week": [5]},
  "reminder_offset": "1h",
  "created_at": "2026-02-07T14:00:00Z"
}
```

**Side effects**:
- Publishes TaskEvent (type: "created") to task-events topic
- If reminder_offset set: publishes ReminderEvent to reminders topic
  and schedules Dapr Job

**Errors**: 401, 422 (validation), 503

---

### GET /api/tasks/{task_id}

Get a single task by ID.

**Response** (200): Full task object (same schema as list item)

**Errors**: 401, 404 Not Found

---

### PATCH /api/tasks/{task_id}

Update a task. Publishes "updated" event.

**Request** (partial update — only include changed fields):
```json
{
  "title": "Buy organic groceries",
  "priority": "medium",
  "tags": ["shopping", "organic"]
}
```

**Response** (200): Updated full task object

**Side effects**:
- Publishes TaskEvent (type: "updated") to task-events topic
- If due_date or reminder_offset changed: cancels old reminder,
  creates new one

**Errors**: 401, 404, 422, 503

---

### POST /api/tasks/{task_id}/complete

Mark a task as completed. Publishes "completed" event.

**Response** (200):
```json
{
  "id": 123,
  "status": "completed",
  "completed_at": "2026-02-07T15:30:00Z"
}
```

**Side effects**:
- Publishes TaskEvent (type: "completed") to task-events topic
- If recurring: Recurring Task Service creates next occurrence
- Cancels any pending reminder
- Creates CompletionRecord

**Errors**: 401, 404, 409 Conflict (already completed)

---

### POST /api/tasks/{task_id}/reopen

Reopen a completed task.

**Response** (200): Task object with status "pending", completed_at null

**Side effects**: Publishes TaskEvent (type: "updated")

**Errors**: 401, 404, 409 (not completed)

---

### DELETE /api/tasks/{task_id}

Delete a task. Publishes "deleted" event.

**Response** (204): No content

**Side effects**:
- Publishes TaskEvent (type: "deleted")
- Cancels any pending reminder
- Removes associated TaskTag rows

**Errors**: 401, 404

---

## Tag Endpoints

### GET /api/tags

List all tags for the current user (for autocomplete).

**Query Parameters**:

| Parameter | Type   | Required | Description                     |
|-----------|--------|----------|---------------------------------|
| q         | string | No       | Prefix search for autocomplete  |

**Response** (200):
```json
{
  "tags": [
    {"id": 1, "name": "work", "task_count": 15},
    {"id": 2, "name": "personal", "task_count": 8}
  ]
}
```

---

## Task History Endpoint

### GET /api/tasks/{task_id}/completions

Get completion history for a recurring task.

**Response** (200):
```json
{
  "completions": [
    {"id": 1, "completed_at": "2026-02-06T08:00:00Z", "completed_by": "uuid"},
    {"id": 2, "completed_at": "2026-02-07T08:15:00Z", "completed_by": "uuid"}
  ]
}
```

**Errors**: 401, 404

---

## Health Endpoints

### GET /healthz

Liveness probe.

**Response** (200): `{"status": "ok"}`

### GET /readyz

Readiness probe. Checks DB connection and Dapr sidecar availability.

**Response** (200): `{"status": "ready", "checks": {"database": "ok", "dapr": "ok"}}`
**Response** (503): `{"status": "not_ready", "checks": {"database": "ok", "dapr": "unavailable"}}`
