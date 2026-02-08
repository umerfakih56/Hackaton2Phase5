---
id: 001
title: Create Project Constitution
stage: constitution
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: user
command: /sp.constitution
labels: ["constitution", "governance", "project-setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
---

## Prompt

Purpose:
Transform the Todo Chatbot from a monolithic application into a distributed, event-driven, cloud-native system that demonstrates enterprise-grade architecture patterns.
Non-Negotiable Principles:

Spec-Driven Development First

No manual coding allowed
All implementation via Claude Code following Agentic Dev Stack workflow
Specification → Plan → Tasks → Implement cycle strictly enforced


Event-Driven Architecture

All inter-service communication via Kafka events
Services must be loosely coupled
Events follow standardized schema
Pub/Sub pattern for all async operations


Cloud-Native Design

Containerized workloads only (Docker)
Kubernetes-native deployment (Minikube → Cloud)
Horizontal scalability built-in
12-factor app principles


Dapr Abstraction Layer

Infrastructure access ONLY through Dapr building blocks
No direct Kafka/DB/Secret libraries in application code
Portable across clouds via YAML configuration
HTTP/gRPC APIs for all infrastructure interactions


Security & Secrets

No hardcoded credentials
Kubernetes Secrets or Dapr SecretStore
JWT authentication maintained from Phase III
Secure communication between services


Observability

Structured logging required
Monitoring and health endpoints
CI/CD pipeline with Github Actions
Deployment tracking



Technology Stack (Non-Negotiable):

Frontend: Next.js 16+ (App Router)
Backend: Python FastAPI with SQLModel
Database: Neon Serverless PostgreSQL
Message Broker: Kafka (Redpanda Cloud/Strimzi on K8s)
Runtime: Dapr (Pub/Sub, State, Jobs API, Secrets, Service Invocation)
Orchestration: Kubernetes (Minikube local → AKS/GKE/OKE cloud)
CI/CD: GitHub Actions
Auth: Better Auth with JWT
AI: OpenAI Agents SDK with MCP Tools

Architecture Constraints:

Stateless application servers
Database as single source of truth
Event sourcing for task operations
Idempotent event handlers
Graceful degradation on service failures

## Response snapshot

Created the project constitution v1.0.0 for the Todo Chatbot Cloud-Native system. The constitution codifies 6 non-negotiable principles (Spec-Driven Development, Event-Driven Architecture, Cloud-Native Design, Dapr Abstraction Layer, Security & Secrets, Observability), the full technology stack, architecture constraints, development workflow, quality gates, and governance rules including amendment procedures and semantic versioning policy. All template placeholders were resolved. Templates were verified for compatibility — no updates required.

## Outcome

- ✅ Impact: Project constitution established as the supreme governance document
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (created)
- 🔁 Next prompts: /sp.specify to create first feature spec
- 🧠 Reflection: Clean initial constitution — all 6 principles mapped from user input with no ambiguity

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
