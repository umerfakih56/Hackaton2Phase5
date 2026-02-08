# Recurring Task Service Contract

**Service**: Recurring Task Service (Python FastAPI)
**Type**: Event consumer (no public API)
**Subscribes to**: task-events topic

## Purpose

Listens for task completion events. When a completed task has
`is_recurring: true`, calculates and creates the next occurrence.

## Subscription Declaration

```
GET /dapr/subscribe

Response:
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/events/task-completed"
  }
]
```

## Event Handler

### POST /events/task-completed

Invoked by Dapr when a task-events message arrives.

**Accepts**: CloudEvents envelope with TaskEvent data

**Processing logic**:

1. Parse event. If `event_type` != "completed", acknowledge (200) and
   skip.
2. If `task_data.is_recurring` is false, acknowledge (200) and skip.
3. Extract `correlation_id`. Check idempotency store. If already
   processed, return 200.
4. Calculate next occurrence date from `recurrence_pattern`:
   - **daily**: current due_date + 1 day
   - **weekly**: next matching day_of_week after current due_date
   - **monthly**: same day_of_month in next month (clamp to last day
     if month is shorter)
   - **custom**: current due_date + interval_days
5. Create new task via Backend API (`POST /api/tasks`) with:
   - Same title, description, tags, priority
   - New due_date = calculated next occurrence
   - `recurrence_pattern.parent_task_id` = original task ID
   - Same reminder_offset (if set)
6. Record `correlation_id` as processed.
7. Return 200 to acknowledge event.

**Error responses**:
- 200: Event processed or skipped (idempotent)
- 500: Processing failed (Dapr will retry)

---

## Health Endpoints

### GET /healthz

**Response** (200): `{"status": "ok"}`

### GET /readyz

**Response** (200): `{"status": "ready", "checks": {"dapr": "ok"}}`

---

## Recurrence Calculation Rules

| Pattern  | Input                 | Next Occurrence                     |
|----------|-----------------------|-------------------------------------|
| daily    | due_date              | due_date + 1 day                    |
| weekly   | due_date, days_of_week| Next matching weekday after due_date|
| monthly  | due_date, day_of_month| Same day next month (clamped)       |
| custom   | due_date, interval    | due_date + interval_days            |

### Edge case: Monthly on 31st

If `day_of_month` = 31 and next month has 30 days, schedule for the
30th. If February (28/29 days), schedule for the last day.

### Edge case: Weekly with multiple days

If `days_of_week` = [0, 2] (Monday, Wednesday) and current completion
is Monday, next occurrence is Wednesday of the same week. If current
is Wednesday, next is Monday of the following week.
