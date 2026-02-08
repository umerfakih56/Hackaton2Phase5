# Implementation Plan: Event-Driven Todo Chatbot

**Branch**: `001-event-driven-todo` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-event-driven-todo/spec.md`

## Summary

Transform the Todo Chatbot from a monolithic application into a
distributed, event-driven, cloud-native system. The system consists of
4 services (Frontend, Backend API, Recurring Task Service, Notification
Service) communicating via Kafka events through Dapr Pub/Sub, deployed
on Kubernetes. Key features: task priorities, tags, search/filter/sort,
due dates with reminders (via Dapr Jobs API), and recurring tasks
(event-driven auto-creation on completion).

## Technical Context

**Language/Version**: Python 3.12+ (backend services), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, httpx, Pydantic (backend); Next.js 16+, Better Auth (frontend)
**Storage**: Neon Serverless PostgreSQL (primary), Dapr State Store (idempotency/cache)
**Testing**: pytest + httpx (backend), vitest + React Testing Library (frontend)
**Target Platform**: Kubernetes (Minikube local, AKS/GKE/OKE cloud)
**Project Type**: Web application (multi-service)
**Performance Goals**: <2s search (10K tasks), <5s recurring task creation, <1min reminder trigger
**Constraints**: All infra via Dapr sidecar, stateless services, idempotent event handlers
**Scale/Scope**: 100 concurrent users, 10K tasks per user, 4 microservices + Kafka + PostgreSQL

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Spec-Driven Dev | Spec exists, plan traces to spec | ✅ PASS |
| II. Event-Driven | All inter-service comms via Kafka Pub/Sub | ✅ PASS — task-events, reminders topics defined |
| III. Cloud-Native | Docker + K8s, stateless, 12-factor | ✅ PASS — Minikube + Helm charts planned |
| IV. Dapr Abstraction | No direct Kafka/secrets libs in app code | ✅ PASS — httpx → Dapr sidecar only |
| V. Security | No hardcoded secrets, JWT auth | ✅ PASS — Dapr Secrets API + Better Auth JWT |
| VI. Observability | Structured logs, health endpoints, CI/CD | ✅ PASS — /healthz, /readyz, JSON logs, GH Actions |

**Architecture Constraints Check**:

| Constraint | Validation | Status |
|------------|-----------|--------|
| Stateless servers | All state in Neon DB or event store | ✅ PASS |
| DB as source of truth | SQLModel → Neon PostgreSQL | ✅ PASS |
| Event sourcing | Every mutation publishes event before read model update | ✅ PASS |
| Idempotent handlers | Correlation ID dedup via Dapr State Store | ✅ PASS |
| Graceful degradation | Outbox pattern for Dapr unavailability | ✅ PASS |

**Post-Phase 1 Re-check**: Direct PostgreSQL driver (asyncpg via
SQLAlchemy) is used for relational data access. This is justified in
research.md R5: Dapr State Store is key-value only and cannot support
relational queries, joins, or full-text search needed for the task
domain. The Dapr abstraction principle applies to infrastructure
services (messaging, secrets, scheduling), not the primary database.

## Project Structure

### Documentation (this feature)

```text
specs/001-event-driven-todo/
├── plan.md              # This file
├── research.md          # Phase 0: technology decisions
├── data-model.md        # Phase 1: entity definitions
├── quickstart.md        # Phase 1: developer setup guide
├── contracts/
│   ├── backend-api.md       # REST API contract
│   ├── event-schemas.md     # Kafka event schemas
│   ├── recurring-task-service.md  # Consumer contract
│   └── notification-service.md    # Consumer + Jobs contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2: /sp.tasks output (not yet created)
```

### Source Code (repository root)

```text
frontend/                       # Next.js 16+ (App Router)
├── src/
│   ├── app/                    # App Router pages and layouts
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Landing / redirect
│   │   ├── (auth)/             # Auth routes (login, register)
│   │   ├── (dashboard)/        # Protected dashboard routes
│   │   │   ├── layout.tsx      # Dashboard layout with sidebar
│   │   │   ├── page.tsx        # Task list view
│   │   │   ├── chat/page.tsx   # Chat interface
│   │   │   └── calendar/page.tsx # Calendar view
│   │   └── api/                # Next.js API routes (Better Auth)
│   ├── components/
│   │   ├── ui/                 # Base UI components
│   │   ├── tasks/              # Task-specific components
│   │   │   ├── task-list.tsx
│   │   │   ├── task-card.tsx
│   │   │   ├── task-form.tsx
│   │   │   ├── priority-badge.tsx
│   │   │   ├── tag-input.tsx
│   │   │   ├── search-bar.tsx
│   │   │   └── filter-panel.tsx
│   │   └── chat/               # Chat components
│   │       ├── chat-panel.tsx
│   │       └── message-list.tsx
│   └── lib/
│       ├── api-client.ts       # HTTP client for backend API
│       ├── auth.ts             # Better Auth configuration
│       └── types.ts            # Shared TypeScript types
├── tests/
├── Dockerfile
└── package.json

backend/                        # FastAPI + SQLModel + MCP
├── app/
│   ├── main.py                 # FastAPI app, Dapr subscription endpoint
│   ├── config.py               # Settings from env vars
│   ├── database.py             # SQLModel engine + session
│   ├── models/
│   │   ├── task.py             # Task SQLModel
│   │   ├── tag.py              # Tag + TaskTag SQLModels
│   │   ├── reminder.py         # Reminder SQLModel
│   │   ├── completion.py       # CompletionRecord SQLModel
│   │   ├── conversation.py     # Conversation + Message SQLModels
│   │   └── user.py             # User SQLModel
│   ├── api/
│   │   ├── tasks.py            # Task CRUD routes
│   │   ├── tags.py             # Tag routes
│   │   ├── chat.py             # Chat endpoint
│   │   ├── health.py           # Health check routes
│   │   └── deps.py             # Dependency injection
│   ├── services/
│   │   ├── task_service.py     # Task business logic
│   │   ├── tag_service.py      # Tag business logic
│   │   ├── search_service.py   # Full-text search
│   │   ├── reminder_service.py # Reminder scheduling
│   │   └── event_publisher.py  # Dapr Pub/Sub publishing
│   └── mcp/
│       ├── tools.py            # MCP tool definitions
│       └── agent.py            # OpenAI Agents SDK setup
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
│   ├── contract/               # API contract tests
│   ├── integration/            # Service integration tests
│   └── unit/                   # Unit tests
├── Dockerfile
└── requirements.txt

services/
├── recurring-task/             # Recurring Task Service
│   ├── app/
│   │   ├── main.py             # FastAPI app + subscription
│   │   ├── config.py
│   │   ├── handlers/
│   │   │   └── task_completed.py   # Event handler
│   │   └── services/
│   │       └── recurrence.py   # Next occurrence calculator
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
└── notification/               # Notification Service
    ├── app/
    │   ├── main.py             # FastAPI app + subscription
    │   ├── config.py
    │   ├── handlers/
    │   │   ├── reminder_scheduled.py  # Event handler
    │   │   └── job_trigger.py         # Dapr Jobs callback
    │   └── services/
    │       └── notifier.py     # Notification logic (simulated)
    ├── tests/
    ├── Dockerfile
    └── requirements.txt

k8s/
├── dapr/
│   └── components/
│       ├── kafka-pubsub.yaml   # Dapr Pub/Sub → Kafka
│       ├── statestore.yaml     # Dapr State → PostgreSQL
│       └── secrets.yaml        # Dapr Secrets → K8s Secrets
└── kafka/
    ├── kafka-cluster.yaml      # Strimzi Kafka CRD
    └── kafka-topics.yaml       # Topic definitions

helm/
├── backend/                    # Backend API Helm chart
├── frontend/                   # Frontend Helm chart
├── recurring-task-service/     # Recurring Task Service chart
└── notification-service/       # Notification Service chart

.github/
└── workflows/
    ├── ci.yml                  # Lint, test, build
    └── deploy.yml              # Deploy to K8s
```

**Structure Decision**: Multi-service web application with separate
frontend/, backend/, and services/ directories. Each service has its
own Dockerfile, dependencies, and tests. Shared infrastructure configs
live in k8s/ and helm/. This structure supports independent deployment
of each service to Kubernetes.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Direct PostgreSQL driver (asyncpg) | Relational queries, full-text search, joins required for task domain | Dapr State Store is key-value only — cannot express WHERE, JOIN, ORDER BY, or tsvector queries (see research.md R5) |
| 4 separate services | Event-driven architecture requires independent consumer services for recurring tasks and notifications | Monolith cannot scale consumers independently or isolate failures per constitution principle II |
| Dapr Jobs API (alpha) | Exact-time reminder scheduling without polling | Cron polling wastes resources and violates spec requirement for exact-time triggers; alpha acceptable for Phase V |
