<!--
  Sync Impact Report
  ==================
  Version change: 0.0.0 → 1.0.0 (MAJOR — initial constitution)
  Modified principles: N/A (first version)
  Added sections:
    - Core Principles (6 principles)
    - Technology Stack & Architecture Constraints
    - Development Workflow
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md — ✅ compatible (Constitution Check
      section will be filled per-feature by /sp.plan)
    - .specify/templates/spec-template.md — ✅ compatible (no changes needed)
    - .specify/templates/tasks-template.md — ✅ compatible (phasing and
      parallel markers align with principles)
  Follow-up TODOs: None
-->

# Todo Chatbot Cloud-Native Constitution

## Core Principles

### I. Spec-Driven Development First

All implementation MUST follow the Specification → Plan → Tasks → Implement
cycle. No manual ad-hoc coding is permitted. Every feature begins with a
specification document, proceeds through architectural planning and task
decomposition, and only then enters implementation.

- Every code change MUST trace back to a task in `tasks.md`.
- Tasks MUST trace back to a plan in `plan.md`.
- Plans MUST trace back to a specification in `spec.md`.
- Deviations from the spec require a formal amendment before implementation.

### II. Event-Driven Architecture

All inter-service communication MUST use Kafka events following the
Pub/Sub pattern. Services MUST be loosely coupled — no direct
synchronous calls between business services for state mutations.

- Events MUST follow a standardized schema (CloudEvents or equivalent).
- Every event MUST include: event type, source, timestamp, correlation ID,
  and payload.
- Services MUST be designed to function independently; failure of one
  service MUST NOT cascade to others.
- All asynchronous operations MUST use the Pub/Sub pattern.

### III. Cloud-Native Design

All workloads MUST be containerized with Docker and deployed to
Kubernetes. The system MUST be horizontally scalable and follow
12-factor app principles.

- Application servers MUST be stateless; all state persists in the
  database or event store.
- Configuration MUST be injected via environment variables or config maps.
- Processes MUST start fast, shut down gracefully, and handle SIGTERM.
- Dev/prod parity MUST be maintained — local Minikube mirrors cloud
  deployment topology.
- Each service MUST expose health check and readiness endpoints.

### IV. Dapr Abstraction Layer

Application code MUST NOT directly import or depend on infrastructure
client libraries (Kafka SDK, database drivers, secret managers).
All infrastructure access MUST go through Dapr building blocks.

- Pub/Sub MUST use Dapr Pub/Sub building block (HTTP/gRPC sidecar API).
- State management MUST use Dapr State Store API where applicable.
- Secrets MUST be retrieved via Dapr Secrets API.
- Service-to-service invocation MUST use Dapr Service Invocation API.
- Scheduled jobs MUST use Dapr Jobs API.
- Infrastructure swaps (e.g., Kafka → RabbitMQ) MUST require only YAML
  configuration changes, zero application code changes.

### V. Security & Secrets

No credentials, tokens, or secrets MUST be hardcoded in source code,
container images, or configuration files checked into version control.

- Secrets MUST be stored in Kubernetes Secrets or Dapr SecretStore.
- JWT authentication MUST be maintained for all user-facing endpoints.
- Inter-service communication MUST be authenticated (mTLS or Dapr
  identity).
- All secret references MUST use environment variables or Dapr Secrets
  API at runtime.
- `.env` files are permitted for local development only and MUST be
  listed in `.gitignore`.

### VI. Observability

Every service MUST emit structured logs, expose health/metrics
endpoints, and support distributed tracing.

- Logs MUST be structured (JSON format) with correlation IDs.
- Every service MUST expose `/healthz` (liveness) and `/readyz`
  (readiness) endpoints.
- CI/CD pipelines via GitHub Actions MUST gate deployments on test
  passage and lint checks.
- Deployment events MUST be tracked and auditable.

## Technology Stack & Architecture Constraints

### Non-Negotiable Stack

| Layer             | Technology                                    |
|-------------------|-----------------------------------------------|
| Frontend          | Next.js 16+ (App Router)                      |
| Backend           | Python FastAPI with SQLModel                   |
| Database          | Neon Serverless PostgreSQL                     |
| Message Broker    | Kafka (Redpanda Cloud / Strimzi on K8s)        |
| Runtime           | Dapr (Pub/Sub, State, Jobs, Secrets, Invocation)|
| Orchestration     | Kubernetes (Minikube local, AKS/GKE/OKE cloud) |
| CI/CD             | GitHub Actions                                 |
| Auth              | Better Auth with JWT                           |
| AI                | OpenAI Agents SDK with MCP Tools               |

### Architecture Constraints

- Application servers MUST be stateless.
- The database is the single source of truth for all persistent state.
- Task operations MUST use event sourcing — every mutation produces an
  event before updating the read model.
- Event handlers MUST be idempotent — processing the same event twice
  MUST NOT produce side effects.
- Services MUST degrade gracefully on downstream failures (circuit
  breaker, retry with backoff, fallback responses).

## Development Workflow

### Mandatory Process

1. **Specify**: Create feature spec via `/sp.specify` — define user
   stories, acceptance criteria, and requirements.
2. **Plan**: Generate architecture plan via `/sp.plan` — pass the
   Constitution Check gate before implementation design.
3. **Tasks**: Decompose into ordered tasks via `/sp.tasks` — each task
   is small, testable, and references exact file paths.
4. **Implement**: Execute tasks via `/sp.implement` — follow the task
   list sequentially, commit after each logical unit.

### Quality Gates

- All PRs MUST pass CI (lint, type-check, unit tests, contract tests).
- No direct pushes to `main` — all changes via pull request.
- Every service MUST have at least contract-level tests for its APIs.
- Kubernetes manifests MUST pass `kubectl --dry-run` validation.
- Docker images MUST pass security scanning before deployment.

### Code Standards

- Python: Type hints required, `ruff` for linting, `black` for
  formatting.
- TypeScript/Next.js: Strict mode, `eslint` + `prettier`.
- All API endpoints MUST have OpenAPI documentation.
- Commit messages MUST follow Conventional Commits format.

## Governance

This constitution is the supreme authority for all development decisions
on this project. It supersedes ad-hoc practices, personal preferences,
and external conventions where they conflict.

### Amendment Process

1. Propose amendment with rationale and impact assessment.
2. Document the change with before/after comparison.
3. Update dependent artifacts (specs, plans, tasks) to reflect the
   amendment.
4. Increment constitution version per semantic versioning rules:
   - **MAJOR**: Principle removal, redefinition, or backward-incompatible
     governance change.
   - **MINOR**: New principle added, existing principle materially expanded.
   - **PATCH**: Clarification, typo fix, or non-semantic refinement.

### Compliance

- All PRs and code reviews MUST verify compliance with this constitution.
- Complexity or deviations MUST be justified in the plan's Complexity
  Tracking table.
- Architectural decisions meeting the significance threshold MUST be
  documented as ADRs.

**Version**: 1.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07
