# Tasks: Event-Driven Todo Chatbot

**Input**: Design documents from `/specs/001-event-driven-todo/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: Tests are included where specified in the user's task descriptions.

**Organization**: Tasks are grouped into three major phases (Part A: Features, Part B: Local Deployment, Part C: Cloud Deployment) with sub-phases organized by user story for Part A.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`
- **Backend**: `backend/app/`
- **Recurring Task Service**: `services/recurring-task/app/`
- **Notification Service**: `services/notification/app/`
- **Infrastructure**: `k8s/`, `helm/`, `.github/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and dependency configuration

- [ ] T001 Create project directory structure per plan.md (frontend/, backend/, services/recurring-task/, services/notification/, k8s/, helm/)
- [ ] T002 [P] Initialize backend Python project with FastAPI, SQLModel, httpx, Pydantic, alembic, uvicorn in backend/requirements.txt
- [ ] T003 [P] Initialize frontend Next.js 16+ project with App Router, Better Auth, and Tailwind CSS in frontend/package.json
- [ ] T004 [P] Initialize recurring-task service Python project with FastAPI, httpx in services/recurring-task/requirements.txt
- [ ] T005 [P] Initialize notification service Python project with FastAPI, httpx in services/notification/requirements.txt
- [ ] T006 [P] Create backend config module with env var settings (DATABASE_URL, DAPR_HTTP_PORT, OPENAI_API_KEY) in backend/app/config.py
- [ ] T007 [P] Create .env.example with all required environment variables at project root .env.example
- [ ] T008 [P] Create .gitignore with Python, Node.js, .env, and __pycache__ exclusions at project root .gitignore
- [ ] T009 Configure backend database connection with async SQLModel engine in backend/app/database.py
- [ ] T010 [P] Configure Python linting (ruff) and formatting (black) in backend/pyproject.toml
- [ ] T011 [P] Configure TypeScript strict mode, ESLint, and Prettier in frontend/.eslintrc.json and frontend/tsconfig.json

**Checkpoint**: All projects initialized, dependencies installed, linting configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models, auth, health endpoints, and event publisher — MUST complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T012 Create User SQLModel entity in backend/app/models/user.py per data-model.md
- [ ] T013 Create Task SQLModel entity with priority enum, status enum, due_date, is_recurring, recurrence_pattern JSONB, reminder_offset, search_vector tsvector in backend/app/models/task.py per data-model.md
- [ ] T014 [P] Create Tag and TaskTag SQLModel entities with unique (name, user_id) constraint in backend/app/models/tag.py per data-model.md
- [ ] T015 [P] Create Reminder SQLModel entity with status enum, job_name, unique task_id constraint in backend/app/models/reminder.py per data-model.md
- [ ] T016 [P] Create CompletionRecord SQLModel entity in backend/app/models/completion.py per data-model.md
- [ ] T017 [P] Create Conversation and Message SQLModel entities in backend/app/models/conversation.py per data-model.md
- [ ] T018 Create Alembic migration for all entities with indexes (search_vector GIN, task_user_id, task_status, task_priority, task_due_date, tag_user_name) in backend/alembic/versions/001_initial_schema.py
- [ ] T019 Implement dependency injection (get_session, get_current_user) in backend/app/api/deps.py
- [ ] T020 [P] Implement health check routes GET /healthz and GET /readyz (check DB + Dapr sidecar) in backend/app/api/health.py per contracts/backend-api.md
- [ ] T021 Implement Dapr Pub/Sub event publisher using httpx POST to Dapr sidecar with CloudEvents format in backend/app/services/event_publisher.py per contracts/event-schemas.md
- [ ] T022 Create FastAPI app with CORS, routers, and Dapr subscription endpoint GET /dapr/subscribe in backend/app/main.py
- [ ] T023 [P] Configure Better Auth with JWT in frontend, create auth config in frontend/src/lib/auth.ts
- [ ] T024 [P] Create shared TypeScript types (Task, Tag, Reminder, Priority, TaskEvent) in frontend/src/lib/types.ts per data-model.md
- [ ] T025 [P] Create API client module with authenticated httpx wrapper for backend calls in frontend/src/lib/api-client.ts
- [ ] T026 [P] Create frontend layout with sidebar navigation in frontend/src/app/layout.tsx and frontend/src/app/(dashboard)/layout.tsx
- [ ] T027 Run Alembic migration against Neon database and verify schema: `alembic upgrade head`

**Checkpoint**: Foundation ready — all models, auth, health checks, event publisher, and frontend shell in place

---

## Phase 3: User Story 1 — Task Priorities (Priority: P1) 🎯 MVP

**Goal**: Users can assign High/Medium/Low priority to tasks with color-coded display and priority sorting

**Independent Test**: Create a task, set priority to High, verify color badge. Sort by priority, verify order.

### Implementation for User Story 1

- [ ] T028 [US1] Implement TaskService with create, read, update, complete, delete, reopen operations and priority default ("medium") in backend/app/services/task_service.py
- [ ] T029 [US1] Implement Task CRUD routes (POST /api/tasks, GET /api/tasks, GET /api/tasks/{id}, PATCH /api/tasks/{id}, POST /api/tasks/{id}/complete, POST /api/tasks/{id}/reopen, DELETE /api/tasks/{id}) in backend/app/api/tasks.py per contracts/backend-api.md
- [ ] T030 [US1] Add priority validation (must be high/medium/low) and default value in task creation flow in backend/app/services/task_service.py
- [ ] T031 [US1] Wire event publisher to publish TaskEvent on every task mutation (create/update/complete/delete) in backend/app/services/task_service.py
- [ ] T032 [P] [US1] Create MCP tool definitions for add_task, update_task, complete_task, delete_task, list_tasks with priority parameter in backend/app/mcp/tools.py
- [ ] T033 [P] [US1] Create OpenAI Agents SDK agent setup with MCP tools in backend/app/mcp/agent.py
- [ ] T034 [US1] Implement chat endpoint POST /api/{user_id}/chat that processes messages through the AI agent in backend/app/api/chat.py per contracts/backend-api.md
- [ ] T035 [P] [US1] Create PriorityBadge component with color coding (Red=High, Yellow=Medium, Green=Low) in frontend/src/components/tasks/priority-badge.tsx
- [ ] T036 [P] [US1] Create TaskCard component displaying title, status, priority badge in frontend/src/components/tasks/task-card.tsx
- [ ] T037 [US1] Create TaskList component with priority sort option in frontend/src/components/tasks/task-list.tsx
- [ ] T038 [US1] Create TaskForm component with priority selector (dropdown: High/Medium/Low) in frontend/src/components/tasks/task-form.tsx
- [ ] T039 [US1] Build dashboard task list page fetching from GET /api/tasks with priority display in frontend/src/app/(dashboard)/page.tsx
- [ ] T040 [US1] Verify: create task via chat with priority, confirm default Medium, sort by priority works

**Checkpoint**: Task CRUD with priorities fully functional via chat and UI. MVP deliverable.

---

## Phase 4: User Story 2 — Tags & Categories (Priority: P2)

**Goal**: Users can add free-form tags to tasks, with autocomplete and tag filtering

**Independent Test**: Add tags "work" and "urgent" to a task, filter by "work", verify autocomplete.

### Implementation for User Story 2

- [ ] T041 [US2] Implement TagService with create-or-get, list with prefix search, and tag-task association in backend/app/services/tag_service.py
- [ ] T042 [US2] Implement tag routes GET /api/tags (with ?q= autocomplete) in backend/app/api/tags.py per contracts/backend-api.md
- [ ] T043 [US2] Extend TaskService to handle tag associations on create/update (create-or-get tags, link via TaskTag) in backend/app/services/task_service.py
- [ ] T044 [US2] Extend GET /api/tasks to include tags array in response and support ?tags= filter parameter in backend/app/api/tasks.py
- [ ] T045 [US2] Update MCP tools (add_task, update_task, list_tasks) to accept and return tags parameter in backend/app/mcp/tools.py
- [ ] T046 [P] [US2] Create TagInput component with autocomplete (fetches GET /api/tags?q=) in frontend/src/components/tasks/tag-input.tsx
- [ ] T047 [US2] Integrate TagInput into TaskForm and display tags on TaskCard in frontend/src/components/tasks/task-form.tsx and frontend/src/components/tasks/task-card.tsx
- [ ] T048 [US2] Verify: add tags via chat and UI, autocomplete suggests existing tags, filter by tag works

**Checkpoint**: Tags functional — create, autocomplete, filter, display

---

## Phase 5: User Story 3 — Search, Filter & Sort (Priority: P3)

**Goal**: Full-text search, multi-criteria filtering, and multi-field sorting across tasks

**Independent Test**: Create 10 diverse tasks, search by keyword, filter by priority+tag, sort by due date.

### Implementation for User Story 3

- [ ] T049 [US3] Implement SearchService with tsvector full-text search using plainto_tsquery in backend/app/services/search_service.py
- [ ] T050 [US3] Extend GET /api/tasks to support all query parameters: ?q= (full-text), ?status=, ?priority=, ?tags=, ?due_from=, ?due_to=, ?sort_by=, ?sort_order=, ?page=, ?page_size= in backend/app/api/tasks.py per contracts/backend-api.md
- [ ] T051 [US3] Update list_tasks MCP tool to accept search, filter, and sort parameters in backend/app/mcp/tools.py
- [ ] T052 [P] [US3] Create SearchBar component with text input and search-on-type debounce in frontend/src/components/tasks/search-bar.tsx
- [ ] T053 [P] [US3] Create FilterPanel component with status, priority, tag, and due date range filters in frontend/src/components/tasks/filter-panel.tsx
- [ ] T054 [US3] Integrate SearchBar and FilterPanel into dashboard page with sort controls in frontend/src/app/(dashboard)/page.tsx
- [ ] T055 [US3] Verify: full-text search returns correct results, combined filters work, sort by all fields works, pagination works

**Checkpoint**: Discovery layer complete — search, filter, sort all functional

---

## Phase 6: User Story 4 — Due Dates & Reminders (Priority: P4)

**Goal**: Set due dates with time picker, configure reminders, overdue highlighting, simulated notifications

**Independent Test**: Create task with due date + 1h reminder, verify reminder triggers, verify overdue highlighting.

### Implementation for User Story 4

- [ ] T056 [US4] Implement ReminderService with create, cancel, and compute remind_at from due_date + offset in backend/app/services/reminder_service.py
- [ ] T057 [US4] Extend TaskService to publish ReminderEvent to reminders topic when task has due_date + reminder_offset, and cancel reminder on due_date removal in backend/app/services/task_service.py
- [ ] T058 [US4] Update MCP tools (add_task, update_task) to accept due_date and reminder_offset parameters in backend/app/mcp/tools.py
- [ ] T059 [US4] Add overdue task detection to GET /api/tasks response (flag tasks where due_date < now and status = pending) in backend/app/api/tasks.py
- [ ] T060 [US4] Extend GET /api/tasks to support due_from/due_to filter parameters in backend/app/api/tasks.py
- [ ] T061 [P] [US4] Add date/time picker to TaskForm for due_date and reminder_offset selector in frontend/src/components/tasks/task-form.tsx
- [ ] T062 [P] [US4] Add overdue visual indicator (red highlight) to TaskCard when task is past due in frontend/src/components/tasks/task-card.tsx
- [ ] T063 [US4] Verify: set due date via chat, reminder_offset triggers ReminderEvent publish, overdue tasks highlighted in UI

**Checkpoint**: Due dates and reminder publishing functional

---

## Phase 7: User Story 5 — Recurring Tasks (Priority: P5)

**Goal**: Create recurring tasks (daily/weekly/monthly/custom) that auto-create next occurrence on completion

**Independent Test**: Create daily recurring task, complete it, verify next occurrence auto-created with inherited fields.

### Implementation for User Story 5

- [ ] T064 [US5] Add recurrence_pattern validation to TaskService (validate JSONB schema per type: daily/weekly/monthly/custom rules from data-model.md) in backend/app/services/task_service.py
- [ ] T065 [US5] Extend complete_task to create CompletionRecord and include is_recurring + recurrence_pattern in completed event payload in backend/app/services/task_service.py
- [ ] T066 [US5] Implement GET /api/tasks/{id}/completions endpoint for completion history in backend/app/api/tasks.py per contracts/backend-api.md
- [ ] T067 [US5] Update MCP tools (add_task) to accept is_recurring and recurrence_pattern parameters in backend/app/mcp/tools.py
- [ ] T068 [P] [US5] Add recurrence pattern selector (daily/weekly/monthly/custom) to TaskForm in frontend/src/components/tasks/task-form.tsx
- [ ] T069 [P] [US5] Add completion history view to TaskCard (expandable section showing past completions) in frontend/src/components/tasks/task-card.tsx
- [ ] T070 [US5] Verify: create recurring task via chat, validate recurrence_pattern stored correctly, completion history displays

**Checkpoint**: Recurring task data model and UI complete (auto-creation depends on Phase 8)

---

## Phase 8: User Story 6 — Event-Driven Task Processing (Priority: P6)

**Goal**: Wire Kafka infrastructure, deploy consumer services, verify end-to-end event flow

**Independent Test**: Complete a recurring task, verify "completed" event published, Recurring Task Service creates next occurrence within 5 seconds.

### Infrastructure Setup

- [ ] T071 [US6] Create Strimzi Kafka cluster manifest (single-node for local) in k8s/kafka/kafka-cluster.yaml
- [ ] T072 [US6] Create Kafka topic manifests (task-events, reminders, task-updates) in k8s/kafka/kafka-topics.yaml
- [ ] T073 [P] [US6] Create Dapr Pub/Sub component YAML (kafka-pubsub → Strimzi) in k8s/dapr/components/kafka-pubsub.yaml
- [ ] T074 [P] [US6] Create Dapr State Store component YAML (state.postgresql → Neon) in k8s/dapr/components/statestore.yaml
- [ ] T075 [P] [US6] Create Dapr Secrets component YAML (secretstores.kubernetes) in k8s/dapr/components/secrets.yaml

### Recurring Task Service

- [ ] T076 [US6] Create recurring-task service FastAPI app with /dapr/subscribe, /healthz, /readyz in services/recurring-task/app/main.py per contracts/recurring-task-service.md
- [ ] T077 [US6] Create config module with DAPR_HTTP_PORT and BACKEND_API_URL settings in services/recurring-task/app/config.py
- [ ] T078 [US6] Implement recurrence calculator (daily/weekly/monthly/custom with edge cases: month-end clamping, multi-day weekly) in services/recurring-task/app/services/recurrence.py per contracts/recurring-task-service.md
- [ ] T079 [US6] Implement task-completed event handler with idempotency check (correlation_id via Dapr State Store), recurrence calculation, and new task creation via Backend API in services/recurring-task/app/handlers/task_completed.py per contracts/recurring-task-service.md

### Notification Service

- [ ] T080 [US6] Create notification service FastAPI app with /dapr/subscribe, /healthz, /readyz in services/notification/app/main.py per contracts/notification-service.md
- [ ] T081 [US6] Create config module with DAPR_HTTP_PORT settings in services/notification/app/config.py
- [ ] T082 [US6] Implement reminder-scheduled event handler that schedules Dapr Job via POST to Jobs API in services/notification/app/handlers/reminder_scheduled.py per contracts/notification-service.md
- [ ] T083 [US6] Implement Dapr Jobs callback handler PUT /api/jobs/trigger/reminder-task-{task_id} with simulated notification (structured JSON log) in services/notification/app/handlers/job_trigger.py per contracts/notification-service.md
- [ ] T084 [US6] Implement notifier service (console log simulation of email/push) in services/notification/app/services/notifier.py

### End-to-End Verification

- [ ] T085 [US6] Verify end-to-end: deploy Kafka + Dapr locally via `dapr init`, run all 3 backend services with `dapr run`, create recurring task with reminder, complete task, confirm next occurrence created and reminder fires

**Checkpoint**: Full event-driven pipeline operational — recurring tasks auto-create, reminders trigger

---

## Phase 9: User Story 7 — Dapr Infrastructure Abstraction (Priority: P7)

**Goal**: Verify all infrastructure access goes through Dapr, no direct client libraries

**Independent Test**: Grep codebase for direct Kafka/secret imports — zero matches. Swap Dapr component YAML, confirm app works.

### Implementation for User Story 7

- [ ] T086 [US7] Audit all backend, recurring-task, and notification service code: verify zero imports of kafka-python, confluent-kafka, or any direct Kafka client library
- [ ] T087 [US7] Audit all service code: verify secrets loaded via Dapr Secrets API (httpx GET to Dapr sidecar) or environment variables, not via direct SDK
- [ ] T088 [US7] Implement Dapr Secrets API integration for OPENAI_API_KEY and DATABASE_URL retrieval in backend/app/config.py
- [ ] T089 [US7] Verify Dapr Service Invocation: recurring-task service calls backend API via Dapr invoke endpoint instead of direct HTTP
- [ ] T090 [US7] Verify portability: change kafka-pubsub.yaml component type from pubsub.kafka to pubsub.redis (or similar), confirm application starts and Pub/Sub still works without code changes

**Checkpoint**: Dapr abstraction verified — zero direct infrastructure client libs, component swap works

---

## Phase 10: Dashboard & UI Polish

**Goal**: Dashboard statistics, calendar view, and UI polish

**Independent Test**: Open dashboard, verify stats cards show correct counts, calendar displays tasks by due date.

### Implementation

- [ ] T091 Implement dashboard statistics endpoint GET /api/tasks/dashboard (total, pending, completed, overdue, high priority counts) in backend/app/api/tasks.py
- [ ] T092 [P] Create dashboard page with stat cards (Total, Pending, Completed, Overdue, High Priority) in frontend/src/app/(dashboard)/page.tsx
- [ ] T093 [P] Create ChatPanel and MessageList components for the chatbot interface in frontend/src/components/chat/chat-panel.tsx and frontend/src/components/chat/message-list.tsx
- [ ] T094 [P] Build chat page connecting to POST /api/{user_id}/chat in frontend/src/app/(dashboard)/chat/page.tsx
- [ ] T095 [P] Build calendar view page displaying tasks by due date in frontend/src/app/(dashboard)/calendar/page.tsx
- [ ] T096 Add quick filters (Today, This Week, High Priority) to dashboard page in frontend/src/app/(dashboard)/page.tsx
- [ ] T097 Verify: dashboard stats match actual task data, chat works end-to-end, calendar shows tasks correctly

**Checkpoint**: Full UI complete — dashboard, chat, calendar, task management

---

## Phase 11: Containerization & Local Deployment (Part B)

**Purpose**: Dockerize all services and deploy to Minikube via Helm

### Containerization

- [ ] T098 [P] Create multi-stage Dockerfile for backend service in backend/Dockerfile
- [ ] T099 [P] Create multi-stage Dockerfile for frontend (Next.js standalone output) in frontend/Dockerfile
- [ ] T100 [P] Create Dockerfile for recurring-task service in services/recurring-task/Dockerfile
- [ ] T101 [P] Create Dockerfile for notification service in services/notification/Dockerfile
- [ ] T102 Build and test all 4 Docker images locally: `docker build -t todo-backend:latest ./backend` (repeat for each)

### Helm Charts

- [ ] T103 [P] Create Helm chart for backend with Dapr annotations (dapr.io/enabled, dapr.io/app-id, dapr.io/app-port) in helm/backend/
- [ ] T104 [P] Create Helm chart for frontend with ingress configuration in helm/frontend/
- [ ] T105 [P] Create Helm chart for recurring-task-service with Dapr annotations in helm/recurring-task-service/
- [ ] T106 [P] Create Helm chart for notification-service with Dapr annotations in helm/notification-service/
- [ ] T107 Validate all Helm charts: `helm lint helm/backend helm/frontend helm/recurring-task-service helm/notification-service`

### Minikube Deployment

- [ ] T108 Deploy Strimzi operator and Kafka cluster to Minikube: `kubectl apply -f k8s/kafka/`
- [ ] T109 Install Dapr on Minikube: `dapr init -k` and deploy components: `kubectl apply -f k8s/dapr/components/`
- [ ] T110 Deploy all services via Helm: `helm install backend ./helm/backend && helm install frontend ./helm/frontend && helm install recurring-task-service ./helm/recurring-task-service && helm install notification-service ./helm/notification-service`
- [ ] T111 Verify all pods running with Dapr sidecars: `kubectl get pods` and `kubectl logs <pod> daprd`
- [ ] T112 Port-forward and test end-to-end: `kubectl port-forward svc/frontend 3000:3000`, create recurring task with reminder, complete it, verify next occurrence and reminder trigger

### Dapr Integration Test

- [ ] T113 Test Pub/Sub: publish event via Dapr API, verify consumer receives it
- [ ] T114 Test State Store: save and retrieve state via Dapr State API
- [ ] T115 Test Jobs API: schedule job, verify callback fires on notification service
- [ ] T116 Test Secrets: retrieve secret via Dapr Secrets API, verify app uses it

**Checkpoint**: All services running on Minikube, full event-driven flow operational

---

## Phase 12: Cloud Deployment (Part C)

**Purpose**: Deploy to cloud Kubernetes cluster with CI/CD

### Cloud Infrastructure

- [ ] T117 Provision cloud Kubernetes cluster (AKS/GKE/OKE) and configure kubectl access
- [ ] T118 Install Dapr on cloud cluster: `dapr init -k`
- [ ] T119 Deploy Kafka on cloud: Strimzi operator on cloud cluster OR configure Redpanda Cloud with connection credentials
- [ ] T120 Create cloud-specific Dapr component YAMLs with cloud Kafka credentials in k8s/dapr/components/ (copy and update from local)
- [ ] T121 Deploy Dapr components to cloud: `kubectl apply -f k8s/dapr/components/`

### Application Deployment

- [ ] T122 Push Docker images to container registry (Docker Hub, ACR, GCR, or OCIR)
- [ ] T123 Create values-cloud.yaml for each Helm chart with cloud image registry, replica counts, and resource limits
- [ ] T124 Deploy all services to cloud via Helm: `helm install <release> ./helm/<chart> -f values-cloud.yaml`
- [ ] T125 Expose frontend via LoadBalancer or Ingress, verify public URL accessible
- [ ] T126 Test end-to-end on cloud: create task via chat, complete recurring task, verify reminder fires

### CI/CD

- [ ] T127 Create GitHub Actions CI workflow (lint, type-check, test, build Docker images) in .github/workflows/ci.yml
- [ ] T128 Create GitHub Actions deploy workflow (push to registry, helm upgrade on cloud cluster) in .github/workflows/deploy.yml
- [ ] T129 Configure GitHub repository secrets (DOCKER_REGISTRY, KUBE_CONFIG, DATABASE_URL)
- [ ] T130 Test CI/CD pipeline: push commit, verify build + test + deploy succeeds

**Checkpoint**: Application live on cloud with automated CI/CD pipeline

---

## Phase 13: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements across all services

- [ ] T131 [P] Add structured JSON logging with correlation IDs to all backend services (backend, recurring-task, notification)
- [ ] T132 [P] Add OpenAPI documentation annotations to all backend API endpoints in backend/app/api/*.py
- [ ] T133 Run quickstart.md validation: follow the guide end-to-end on a fresh environment, fix any issues
- [ ] T134 Security hardening: verify .env in .gitignore, no secrets in source code, JWT validation on all endpoints
- [ ] T135 Performance check: test search with 10K tasks (< 2s target), verify filters (< 1s target)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phases 3-5 (US1-US3: Priorities, Tags, Search)**: Depend on Phase 2. US1 first (MVP), then US2, then US3 (US3 depends on US1+US2 for full filter value)
- **Phase 6 (US4: Due Dates)**: Depends on Phase 2. Can parallel with US1-US3 for backend, needs US1 UI patterns
- **Phase 7 (US5: Recurring Tasks)**: Depends on Phase 6 (due date infrastructure)
- **Phase 8 (US6: Event-Driven)**: Depends on Phases 3-7 (all features exist). Wires Kafka + Dapr consumers
- **Phase 9 (US7: Dapr Abstraction)**: Depends on Phase 8 (all Dapr usage exists to audit)
- **Phase 10 (Dashboard)**: Depends on Phases 3-7 (features exist for stats). Can start UI work after Phase 3
- **Phase 11 (Local Deploy)**: Depends on Phase 8 (all services built)
- **Phase 12 (Cloud Deploy)**: Depends on Phase 11 (Helm charts validated locally)
- **Phase 13 (Polish)**: Depends on Phase 12 (all features deployed)

### User Story Dependencies

- **US1 (Priorities)**: Phase 2 complete → start immediately. No cross-story dependencies.
- **US2 (Tags)**: Phase 2 complete → can start after US1 or in parallel (different files).
- **US3 (Search/Filter/Sort)**: Benefits from US1 + US2 being complete (priority/tag filters).
- **US4 (Due Dates)**: Phase 2 complete → independent of US1-US3. Due date column already in Task model.
- **US5 (Recurring Tasks)**: Depends on US4 (due date used for next occurrence calculation).
- **US6 (Event-Driven)**: Depends on US5 (recurring task logic needed for consumer). Wires all previous stories into Kafka.
- **US7 (Dapr Abstraction)**: Depends on US6 (all Dapr usage in place for audit).

### Within Each User Story

- Models before services
- Services before API routes
- API routes before MCP tools
- MCP tools before chat integration
- Backend before frontend components
- Core implementation before integration testing

### Parallel Opportunities

- Phase 1: All setup tasks T002-T011 marked [P] can run in parallel
- Phase 2: Models T014-T017 in parallel; auth T023-T026 in parallel with backend models
- Phase 3 (US1): MCP tools T032-T033 in parallel; UI components T035-T036 in parallel
- Phase 4 (US2): TagInput T046 in parallel with other UI work
- Phase 5 (US3): SearchBar T052 and FilterPanel T053 in parallel
- Phase 6 (US4): Date picker T061 and overdue indicator T062 in parallel
- Phase 7 (US5): Recurrence selector T068 and completion history T069 in parallel
- Phase 8 (US6): Dapr component YAMLs T073-T075 in parallel; services can develop in parallel after infra
- Phase 11: All Dockerfiles T098-T101 in parallel; all Helm charts T103-T106 in parallel

---

## Implementation Strategy

### MVP First (Phase 1-3: Setup → Foundation → Priorities)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T027)
3. Complete Phase 3: User Story 1 — Priorities (T028-T040)
4. **STOP and VALIDATE**: Task CRUD with priorities works via chat and UI
5. Deploy/demo if ready — this is a functional MVP

### Incremental Feature Delivery

1. Setup + Foundation → ready
2. + US1 (Priorities) → MVP with priority management
3. + US2 (Tags) → organizational tagging
4. + US3 (Search/Filter/Sort) → full discovery layer
5. + US4 (Due Dates) → time-aware tasks with reminders
6. + US5 (Recurring Tasks) → automated task recurrence
7. + US6 (Event-Driven) → Kafka + Dapr event pipeline
8. + US7 (Dapr Audit) → portability verified

### Cloud Readiness Path

1. Complete all Part A features (Phases 1-10)
2. Containerize (Phase 11: Dockerfiles + Helm)
3. Deploy locally to Minikube (Phase 11: verify)
4. Deploy to cloud (Phase 12: AKS/GKE/OKE)
5. Set up CI/CD (Phase 12: GitHub Actions)
6. Polish (Phase 13: logging, docs, security)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after its phase
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 135
- Tasks per story: US1=13, US2=8, US3=7, US4=8, US5=7, US6=15, US7=5
- Setup/Foundation: 27, Dashboard: 7, Containerization: 19, Cloud: 14, Polish: 5
