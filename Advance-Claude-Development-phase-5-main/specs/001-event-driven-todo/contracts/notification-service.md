# Notification Service Contract

**Service**: Notification Service (Python FastAPI)
**Type**: Event consumer + Dapr Jobs callback receiver
**Subscribes to**: reminders topic

## Purpose

Handles reminder delivery. Receives scheduled job callbacks from Dapr
Jobs API at the configured reminder time and triggers notifications
(simulated in Phase V via console log / in-app notification).

## Subscription Declaration

```
GET /dapr/subscribe

Response:
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "reminders",
    "route": "/events/reminder-scheduled"
  }
]
```

## Endpoints

### POST /events/reminder-scheduled

Invoked by Dapr when a reminder event arrives on the reminders topic.

**Processing logic**:

1. Parse ReminderEvent from CloudEvents envelope.
2. Schedule a Dapr Job for the `remind_at` time:
   ```
   POST http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/reminder-task-{task_id}
   {
     "dueTime": "{remind_at_iso8601}",
     "data": {
       "task_id": {task_id},
       "title": "{title}",
       "user_id": "{user_id}",
       "due_at": "{due_at}"
     }
   }
   ```
3. If `remind_at` is in the past (< 5 minutes), trigger immediately.
4. Return 200.

**Error responses**:
- 200: Job scheduled or triggered
- 500: Scheduling failed (Dapr will retry delivery)

---

### PUT /api/jobs/trigger/reminder-task-{task_id}

Callback endpoint invoked by Dapr Jobs API when the scheduled time
arrives.

**Request** (from Dapr Jobs):
```json
{
  "task_id": 123,
  "title": "Buy groceries",
  "user_id": "uuid",
  "due_at": "2026-02-08T10:00:00Z"
}
```

**Processing logic**:

1. Log notification: `[REMINDER] Task "Buy groceries" due at 2026-02-08T10:00:00Z for user {user_id}`
2. Update Reminder status to "triggered" in database.
3. Publish audit event to task-events topic (optional).
4. Return 200.

**Phase V simulation**: Notification is logged to stdout (structured
JSON log) and optionally pushed to the frontend via a notification
endpoint or WebSocket.

---

### DELETE /api/jobs/reminder-task-{task_id}

Cancel a scheduled reminder job.

**Processing logic**:

1. Delete the Dapr Job:
   ```
   DELETE http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/reminder-task-{task_id}
   ```
2. Update Reminder status to "cancelled".
3. Return 200.

---

## Health Endpoints

### GET /healthz

**Response** (200): `{"status": "ok"}`

### GET /readyz

**Response** (200): `{"status": "ready", "checks": {"dapr": "ok"}}`
