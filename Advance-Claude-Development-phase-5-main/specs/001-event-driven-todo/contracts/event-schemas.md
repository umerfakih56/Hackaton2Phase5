# Event Schemas Contract

**Feature Branch**: `001-event-driven-todo`
**Date**: 2026-02-07
**Transport**: Dapr Pub/Sub (backed by Kafka)

## Topics

| Topic         | Purpose                              | Producers      | Consumers                    |
|---------------|--------------------------------------|----------------|------------------------------|
| task-events   | All task CRUD mutations              | Backend API    | Recurring Task Svc, Audit    |
| reminders     | Reminder scheduling and triggers     | Backend API    | Notification Svc             |

---

## TaskEvent Schema (topic: task-events)

Published on every task mutation (create, update, complete, delete).

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/tasks",
  "id": "uuid-correlation-id",
  "time": "2026-02-07T14:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "created",
    "task_id": 123,
    "task_data": {
      "id": 123,
      "title": "Buy groceries",
      "description": "Weekly grocery shopping",
      "status": "pending",
      "priority": "medium",
      "tags": ["shopping"],
      "due_date": "2026-02-08T10:00:00Z",
      "is_recurring": true,
      "recurrence_pattern": {
        "type": "weekly",
        "days_of_week": [5]
      },
      "reminder_offset": "1h"
    },
    "user_id": "uuid-string",
    "timestamp": "2026-02-07T14:30:00Z"
  }
}
```

### Event Types

| event_type  | CloudEvents type           | Trigger                    |
|-------------|----------------------------|----------------------------|
| created     | com.todo.task.created      | New task created           |
| updated     | com.todo.task.updated      | Task fields modified       |
| completed   | com.todo.task.completed    | Task marked complete       |
| deleted     | com.todo.task.deleted      | Task removed               |

### Required Fields

| Field          | Type     | Description                          |
|----------------|----------|--------------------------------------|
| event_type     | string   | One of: created/updated/completed/deleted |
| task_id        | integer  | The affected task's ID               |
| task_data      | object   | Full task snapshot at event time     |
| user_id        | string   | UUID of the user who triggered       |
| timestamp      | string   | ISO 8601 datetime with timezone      |

---

## ReminderEvent Schema (topic: reminders)

Published when a reminder is created or rescheduled.

```json
{
  "specversion": "1.0",
  "type": "com.todo.reminder.scheduled",
  "source": "/api/tasks",
  "id": "uuid-correlation-id",
  "time": "2026-02-07T14:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 123,
    "title": "Buy groceries",
    "due_at": "2026-02-08T10:00:00Z",
    "remind_at": "2026-02-08T09:00:00Z",
    "user_id": "uuid-string"
  }
}
```

### Required Fields

| Field      | Type     | Description                          |
|------------|----------|--------------------------------------|
| task_id    | integer  | The task this reminder belongs to    |
| title      | string   | Task title (for notification display)|
| due_at     | string   | ISO 8601 task due date               |
| remind_at  | string   | ISO 8601 when to trigger reminder    |
| user_id    | string   | UUID of the task owner               |

---

## Dapr Pub/Sub Contract

### Publishing Events

All event publishing MUST use the Dapr Pub/Sub HTTP API:

```
POST http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsub-name}/{topic}
Content-Type: application/cloudevents+json

{CloudEvents envelope}
```

Where `{pubsub-name}` = `kafka-pubsub` (configured in Dapr component).

### Subscribing to Events

Services declare subscriptions via the programmatic API:

```
GET /dapr/subscribe

Response:
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/events/task-events"
  }
]
```

Dapr delivers events to the declared route endpoint on the service.

---

## Idempotency Contract

Every consumer MUST implement idempotent event handling:

1. Extract `correlation_id` from the CloudEvents `id` field.
2. Check if this `correlation_id` has been processed before (using a
   processed-events table or Dapr State Store).
3. If already processed, acknowledge the event and return 200 (no-op).
4. If new, process the event and record the `correlation_id`.
5. Use database transactions to ensure atomicity of processing +
   recording.

---

## Error Handling Contract

### Publisher Errors

- If Dapr sidecar is unavailable (503), the service MUST:
  1. Persist the task mutation to the database (do NOT block the user).
  2. Queue the event for retry (outbox pattern or Dapr retry policy).
  3. Log a warning with correlation ID.

### Consumer Errors

- If event processing fails, return a non-200 status to Dapr.
- Dapr will retry delivery based on the resiliency policy.
- After max retries, the event goes to a dead-letter topic.
- Dead-letter events MUST be monitored and alerted on.
