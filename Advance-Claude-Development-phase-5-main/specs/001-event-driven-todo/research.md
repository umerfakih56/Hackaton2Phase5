# Research: Event-Driven Todo Chatbot

**Feature Branch**: `001-event-driven-todo`
**Date**: 2026-02-07
**Purpose**: Resolve technical unknowns and validate architecture decisions

## R1: Dapr Runtime Version & Jobs API

**Decision**: Use Dapr v1.14+ (latest stable)

**Rationale**: Dapr 1.14 is the latest stable release with mature
Pub/Sub, State Store, Secrets, and Service Invocation building blocks.
The Jobs API is in alpha (v1.0-alpha1 endpoint) but functional for
scheduled job callbacks — suitable for Phase V since exact-time
triggering is the primary use case.

**Alternatives considered**:
- Dapr Workflows (beta) — too complex for simple scheduling
- Cron-based polling — violates the spec requirement for exact-time
  triggers and wastes resources

**Jobs API endpoint**:
```
POST http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job-name}
```
The alpha status is acceptable for Phase V (development/demo). For
production, a fallback to Dapr Pub/Sub with delayed delivery or
external scheduler would be needed.

---

## R2: Kafka on Kubernetes — Strimzi vs Redpanda

**Decision**: Strimzi for local/K8s, Redpanda Cloud option for managed

**Rationale**: Strimzi is the standard Kafka operator for Kubernetes
with full Kafka protocol compatibility. It provides CRDs for Kafka
clusters, topics, and users. For local Minikube, a single-node Strimzi
cluster is sufficient. Redpanda Cloud is a managed option for cloud
deployment but adds cost.

**Alternatives considered**:
- Redpanda on K8s — simpler binary but less Kafka ecosystem tooling
- Confluent Platform — overkill for Phase V scope
- Self-managed Kafka without operator — harder to manage on K8s

**Local setup**: Single-node Strimzi ephemeral cluster (no ZooKeeper
in KRaft mode if Strimzi supports it, otherwise standard 1-broker +
1-ZK setup).

---

## R3: Full-Text Search Strategy in PostgreSQL

**Decision**: PostgreSQL tsvector with GIN index

**Rationale**: For up to 10,000 tasks (SC-002 target), PostgreSQL's
built-in full-text search with tsvector/tsquery is performant and
requires no external dependencies. A GIN index on a generated tsvector
column combining title + description provides sub-second search.

**Alternatives considered**:
- ILIKE with pg_trgm — simpler but slower for prefix/phrase search;
  suitable for autocomplete (tags) but not full-text
- ElasticSearch/Meilisearch — overkill for 10K rows; adds operational
  complexity; violates the Dapr abstraction principle (no direct client
  libs)
- Application-level filtering — poor performance at scale

**Implementation**:
```sql
ALTER TABLE tasks ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
  ) STORED;
CREATE INDEX idx_task_search ON tasks USING GIN(search_vector);
```

For tag autocomplete, use ILIKE with pg_trgm on the tags table (small
dataset, prefix matching is ideal).

---

## R4: Dapr Pub/Sub with FastAPI Integration

**Decision**: Programmatic subscription via `/dapr/subscribe` endpoint

**Rationale**: FastAPI services declare their subscriptions by exposing
a `GET /dapr/subscribe` endpoint that returns a JSON array of
subscription definitions. Dapr calls this on startup to learn which
topics and routes to deliver to.

**Event delivery flow**:
1. Dapr sidecar calls `GET /dapr/subscribe` on app startup
2. Service returns: `[{"pubsubname": "kafka-pubsub", "topic": "task-events", "route": "/events/task-events"}]`
3. When events arrive, Dapr POSTs CloudEvents to the declared route
4. Service processes and returns 200 (success), 404 (drop), or other
   (retry)

**Publishing**:
```python
import httpx

async def publish_event(topic: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/kafka-pubsub/{topic}",
            json=data,
            headers={"Content-Type": "application/cloudevents+json"}
        )
```

**Key**: Use `httpx` (async HTTP client) for Dapr sidecar calls —
NOT kafka-python, confluent-kafka, or any direct Kafka library.

---

## R5: Dapr State Store vs Direct PostgreSQL

**Decision**: Use SQLModel/SQLAlchemy for primary data; Dapr State
Store only for idempotency tracking and ephemeral state

**Rationale**: The application already uses SQLModel for rich
relational data (tasks, tags, recurrence rules, reminders). Dapr State
Store (backed by PostgreSQL) is a key-value abstraction that cannot
express relational queries, joins, or full-text search. Using it as
the primary data store would sacrifice query capability.

**Use Dapr State Store for**:
- Processed event correlation IDs (idempotency tracking)
- Conversation state caching (optional)
- Any ephemeral/non-relational state

**Use SQLModel directly for**:
- Task CRUD with complex queries (filters, sorts, full-text search)
- Tag management with many-to-many relationships
- Reminder and completion history

**Trade-off**: This means the backend service does use a PostgreSQL
driver (asyncpg via SQLAlchemy). This is acceptable because the
constitution's Dapr principle targets infrastructure services (Kafka,
secrets, scheduling) — the database is the source of truth and needs
relational access. The Dapr State Store is used for state management
patterns, not as a replacement for the primary database.

---

## R6: Better Auth with Next.js

**Decision**: Use Better Auth for authentication with JWT tokens

**Rationale**: Better Auth is a modern, framework-agnostic
authentication library that works with Next.js App Router. It supports
JWT tokens for stateless authentication, which aligns with the
constitution's requirement for stateless application servers.

**Integration pattern**:
- Better Auth runs in the Next.js frontend
- JWT tokens are sent to the FastAPI backend in Authorization headers
- Backend validates JWT tokens using the shared secret or public key
- No session storage needed on the backend (stateless)

**Alternatives considered**:
- NextAuth.js — more established but heavier, session-based by default
- Custom JWT — more control but more maintenance
- Clerk/Auth0 — SaaS dependency, adds cost

---

## R7: Recurrence Pattern Storage

**Decision**: JSONB column on the Task table

**Rationale**: A JSONB column provides flexible schema for different
recurrence types while keeping the data model simple. The recurrence
pattern is always read/written as a unit with its task, so
co-location in the same row avoids joins. PostgreSQL's JSONB supports
indexing and querying if needed.

**Schema**:
```json
{
  "type": "daily" | "weekly" | "monthly" | "custom",
  "days_of_week": [0, 2, 4],
  "day_of_month": 15,
  "interval_days": 3,
  "parent_task_id": null
}
```

**Alternatives considered**:
- Separate RecurrenceRule table — adds complexity with no query benefit
  since rules are always fetched with their task
- RFC 5545 RRULE string — powerful but complex to parse; overkill for
  the four supported patterns (daily/weekly/monthly/custom)
- PostgreSQL enum + columns — rigid schema, harder to extend

**Validation**: Application-level validation enforces that the correct
fields are present for each recurrence type (e.g., weekly requires
days_of_week).
