---
id: 003
title: Architecture Plan Event-Driven Todo
stage: plan
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 001-event-driven-todo
branch: 001-event-driven-todo
user: user
command: /sp.plan
labels: ["plan", "architecture", "event-driven", "microservices", "dapr", "kafka"]
links:
  spec: specs/001-event-driven-todo/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-event-driven-todo/plan.md
  - specs/001-event-driven-todo/research.md
  - specs/001-event-driven-todo/data-model.md
  - specs/001-event-driven-todo/quickstart.md
  - specs/001-event-driven-todo/contracts/backend-api.md
  - specs/001-event-driven-todo/contracts/event-schemas.md
  - specs/001-event-driven-todo/contracts/recurring-task-service.md
  - specs/001-event-driven-todo/contracts/notification-service.md
tests:
---

## Prompt

System Architecture with component breakdown covering: Frontend Service (Next.js + Better Auth), Backend API Service (FastAPI + MCP + Dapr Pub/Sub), Recurring Task Service (event consumer for task completion), Notification Service (Dapr Jobs callbacks), Kafka Cluster (Strimzi on K8s), and Neon Database. Includes data flow examples for creating recurring tasks with reminders and completing recurring tasks. Deployment strategy for Minikube (local) and cloud (AKS/GKE/OKE). API specifications for MCP tools (add_task, complete_task, etc.) with new parameters for priority, tags, due_date, reminder_time, is_recurring, and recurrence_pattern.

## Response snapshot

Created the full implementation plan with 8 artifacts:
1. **plan.md** — Technical context, constitution check (all 6 principles PASS), project structure (4-service architecture: frontend, backend, recurring-task, notification), and complexity tracking (3 justified deviations).
2. **research.md** — 7 technology decisions: Dapr v1.14+ with alpha Jobs API, Strimzi for Kafka, PostgreSQL tsvector for search, programmatic Dapr subscriptions, SQLModel for relational data + Dapr State for idempotency, Better Auth with JWT, JSONB for recurrence patterns.
3. **data-model.md** — 9 entities (User, Task, Tag, TaskTag, RecurrenceRule as JSONB, Reminder, CompletionRecord, Conversation, Message) with full field definitions, indexes, validation rules, and event schemas.
4. **contracts/** — 4 contract files: Backend API (15 REST endpoints), Event Schemas (CloudEvents format, task-events + reminders topics), Recurring Task Service (consumer), Notification Service (consumer + Dapr Jobs callback).
5. **quickstart.md** — Developer setup guide covering Minikube, Dapr, Strimzi Kafka, database migrations, service startup, and K8s deployment via Helm.

Constitution check passes all 6 principles with 3 justified complexity items documented.

## Outcome

- ✅ Impact: Complete architecture plan with all Phase 0 and Phase 1 artifacts
- 🧪 Tests: N/A (design artifacts)
- 📁 Files: 8 artifacts created in specs/001-event-driven-todo/
- 🔁 Next prompts: /sp.tasks to generate implementation task list
- 🧠 Reflection: User provided exceptionally detailed architecture input including service responsibilities, data flows, and API specs. This reduced research ambiguity to near-zero. Key trade-off documented: direct PostgreSQL driver alongside Dapr for relational query needs.

## Evaluation notes (flywheel)

- Failure modes observed: Research background agent returned empty output; recovered by writing research.md directly from user input and domain knowledge
- Graders run and results (PASS/FAIL): Constitution check — PASS (6/6 principles, 3 justified deviations)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
