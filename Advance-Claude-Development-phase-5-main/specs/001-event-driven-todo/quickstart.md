# Quickstart: Event-Driven Todo Chatbot

**Feature Branch**: `001-event-driven-todo`
**Date**: 2026-02-07

## Prerequisites

- Docker Desktop with Kubernetes enabled (or Minikube installed)
- kubectl CLI
- Dapr CLI (v1.14+)
- Helm 3
- Python 3.12+
- Node.js 22+ (LTS)
- pnpm (for Next.js frontend)
- Git

## 1. Clone and Setup

```bash
git clone <repo-url>
cd phase5
git checkout 001-event-driven-todo
```

## 2. Local Kubernetes Cluster

### Option A: Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
```

### Option B: Docker Desktop Kubernetes

Enable Kubernetes in Docker Desktop settings. No additional setup
needed.

## 3. Install Dapr

```bash
dapr init -k
dapr status -k
```

Verify all Dapr system services are running:
- dapr-operator
- dapr-sentry
- dapr-sidecar-injector
- dapr-placement-server

## 4. Deploy Kafka (Strimzi)

```bash
# Install Strimzi operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka

# Wait for operator to be ready
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=120s

# Deploy Kafka cluster
kubectl apply -f k8s/kafka/kafka-cluster.yaml -n kafka

# Create topics
kubectl apply -f k8s/kafka/kafka-topics.yaml -n kafka
```

## 5. Apply Dapr Components

```bash
kubectl apply -f k8s/dapr/components/
```

This creates:
- `kafka-pubsub` (Pub/Sub component)
- `statestore` (PostgreSQL state store)
- `kubernetes-secrets` (Secrets component)

## 6. Setup Database

```bash
# For local development, use the Neon connection string in .env
cp .env.example .env
# Edit .env with your Neon database URL

# Run migrations
cd backend
python -m alembic upgrade head
```

## 7. Run Services Locally (Development Mode)

### Backend API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500 -- uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Recurring Task Service

```bash
cd services/recurring-task
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
dapr run --app-id recurring-task-service --app-port 8001 --dapr-http-port 3501 -- uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Notification Service

```bash
cd services/notification
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
dapr run --app-id notification-service --app-port 8002 --dapr-http-port 3502 -- uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend available at: http://localhost:3000

## 8. Deploy to Kubernetes

```bash
# Build Docker images
docker build -t todo-backend:latest ./backend
docker build -t todo-recurring:latest ./services/recurring-task
docker build -t todo-notification:latest ./services/notification
docker build -t todo-frontend:latest ./frontend

# For Minikube: load images into Minikube's Docker daemon
eval $(minikube docker-env)
# Then rebuild images, or use: minikube image load <image>

# Deploy via Helm
helm install backend ./helm/backend
helm install recurring-task-service ./helm/recurring-task-service
helm install notification-service ./helm/notification-service
helm install frontend ./helm/frontend

# Verify
kubectl get pods
kubectl get services
```

## 9. Verify Health

```bash
# Backend API
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz

# Recurring Task Service
curl http://localhost:8001/healthz

# Notification Service
curl http://localhost:8002/healthz
```

## 10. Test Event Flow

```bash
# Create a recurring task via chat
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{"message": "Add a daily task to take vitamins at 8am with a 15 minute reminder"}'

# Complete the task
curl -X POST http://localhost:8000/api/tasks/1/complete \
  -H "Authorization: Bearer <jwt-token>"

# Check that recurring task service created next occurrence
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <jwt-token>"
```

## Project Structure

```text
phase5/
├── frontend/                  # Next.js 16+ App Router
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   ├── components/        # React components
│   │   └── lib/               # Client utilities
│   ├── Dockerfile
│   └── package.json
├── backend/                   # FastAPI + SQLModel
│   ├── app/
│   │   ├── main.py            # FastAPI app + Dapr subscription
│   │   ├── models/            # SQLModel entities
│   │   ├── api/               # Route handlers
│   │   ├── services/          # Business logic
│   │   ├── events/            # Event publishing helpers
│   │   └── mcp/               # MCP tool definitions
│   ├── alembic/               # Database migrations
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── services/
│   ├── recurring-task/        # Recurring Task Service
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── notification/          # Notification Service
│       ├── app/
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
├── k8s/
│   ├── dapr/
│   │   └── components/        # Dapr component YAMLs
│   └── kafka/                 # Strimzi Kafka manifests
├── helm/
│   ├── backend/
│   ├── frontend/
│   ├── recurring-task-service/
│   └── notification-service/
├── specs/                     # SDD artifacts
├── .github/
│   └── workflows/             # GitHub Actions CI/CD
└── .env.example
```

## Environment Variables

| Variable            | Description                    | Example                        |
|---------------------|--------------------------------|--------------------------------|
| DATABASE_URL        | Neon PostgreSQL connection     | postgresql://...@neon.tech/... |
| DAPR_HTTP_PORT      | Dapr sidecar HTTP port         | 3500                           |
| OPENAI_API_KEY      | OpenAI API key (via Dapr Secrets) | sk-...                      |
| BETTER_AUTH_SECRET  | Better Auth session secret     | random-secret-string           |
| BETTER_AUTH_URL     | Better Auth base URL           | http://localhost:3000          |
