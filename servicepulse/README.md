# ServicePulse — Production Operations & Incident Management Platform

**Project 1 of 5 — Transformation Engineering Portfolio**

> A production-style operations platform demonstrating complete engineering lifecycle: requirements → architecture → implementation → testing → deployment → observability. Built as a portfolio/demo system, not connected to real production traffic.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-43%20passed-green.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)](#testing)
[![Ruff](https://img.shields.io/badge/linting-ruff-orange.svg)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🔗 **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/KishanR-dev/servicepulse)** · 📖 **[API Documentation](https://huggingface.co/spaces/KishanR-dev/servicepulse/docs)**

---

## Problem Statement

Building reliable production operations systems requires:

- Structured request processing with clear lifecycle management
- Incident management with root cause analysis (RCA) workflows
- Operational observability through structured logging and metrics
- Testable, maintainable architecture designed for evolution

ServicePulse demonstrates these capabilities as a self-contained system suitable for evaluating engineering practices, architecture decisions, and operational thinking.

---

## What This Demonstrates

| Capability | Implementation |
|---|---|
| **Service Request Lifecycle** | Create → Process → Complete/Fail with state machine validation |
| **Incident Management** | Open → Investigate → Mitigate → Resolve with RCA fields |
| **Layered Architecture** | API → Service → Domain → Repository → Database |
| **Structured Logging** | JSON logs with correlation IDs, event types, durations |
| **Prometheus-Compatible Metrics** | Counters, gauges, histograms in text exposition format |
| **Health Monitoring** | Component-level checks (application + database) |
| **API Design** | RESTful, versioned, OpenAPI-documented, error-standardized |
| **Testing** | Unit, integration, API, failure simulation — 89% coverage |
| **Domain-Driven Design** | Enums, state machines, validation separated from persistence |
| **Container-Ready** | Multi-stage Docker build, non-root user, configurable |
| **Failure Simulation** | Controlled fault injection (development-only, double-gated) |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                         │
│  FastAPI routes · validation · error handling        │
│  Correlation ID middleware · metrics middleware      │
├─────────────────────────────────────────────────────┤
│                 Service Layer                       │
│  Business logic · state transitions · logging        │
│  Metrics collection · orchestration                  │
├─────────────────────────────────────────────────────┤
│                 Domain Layer                        │
│  Enums · state machines · validation rules           │
├─────────────────────────────────────────────────────┤
│              Repository Layer                       │
│  SQLAlchemy ORM · query abstraction                  │
├─────────────────────────────────────────────────────┤
│                 Database                            │
│  SQLite (dev/demo) · PostgreSQL-ready config         │
└─────────────────────────────────────────────────────┘
```

See [Architecture Documentation](docs/architecture.md) for full details.

---

## API Overview

All endpoints are under `/api/v1/` with OpenAPI/Swagger documentation at `/docs`.

### Service Requests

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/requests` | Create a service request |
| `GET` | `/api/v1/requests` | List requests (paginated) |
| `GET` | `/api/v1/requests/{id}` | Get request details |
| `PATCH` | `/api/v1/requests/{id}/status` | Update request status |

### Incidents

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/incidents` | Create an incident |
| `GET` | `/api/v1/incidents` | List incidents (paginated) |
| `GET` | `/api/v1/incidents/{id}` | Get incident details |
| `PATCH` | `/api/v1/incidents/{id}` | Update incident (status, RCA) |

### Operational

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check |
| `GET` | `/api/v1/metrics` | Prometheus text format |
| `GET` | `/api/v1/metrics/json` | Metrics as JSON |

---

## Requirements & Design Context

This project was built from documented requirements with traceability:

| ID | Requirement | Status |
|---|---|---|
| FR-001 | Create service request | ✅ Implemented |
| FR-002 | Input validation | ✅ Implemented |
| FR-003 | Persist requests | ✅ Implemented |
| FR-004 | Retrieve request | ✅ Implemented |
| FR-005 | List requests | ✅ Implemented |
| FR-006 | Update request status | ✅ Implemented |
| FR-007 | Incident management | ✅ Implemented |
| FR-008 | Health check | ✅ Implemented |
| FR-009 | Metrics | ✅ Implemented |
| FR-010 | Failure simulation (dev only) | ✅ Implemented |

Full documentation: [Requirements](docs/requirements.md) · [Traceability Matrix](docs/traceability-matrix.md) · [Engineering Decisions](docs/engineering-decisions.md)

---

## Testing & Quality

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run by category
pytest tests/unit/          # Domain logic and validation
pytest tests/integration/   # End-to-end workflows
pytest tests/api/           # HTTP endpoint contracts
pytest tests/failure/       # Failure simulation safety

# Linting
ruff check .
```

**Results:**
- 43 tests passing
- 89% code coverage
- Ruff: all checks passed
- Categories: unit, integration, API, failure simulation

---

## Observability

### Structured Logging

JSON logs with correlation IDs for request tracing:

```json
{
  "timestamp": "2025-07-08T10:00:00+00:00",
  "level": "INFO",
  "event": "REQUEST_CREATED",
  "request_id": "REQ-000001",
  "correlation_id": "abc12345"
}
```

### Metrics

Prometheus-compatible endpoint at `/api/v1/metrics`:

- `requests_total` — Total service requests created
- `requests_by_status` — Requests grouped by current status
- `incidents_open` — Currently open incidents
- `http_requests_total` — HTTP request count by method/endpoint/status
- `http_request_duration` — Request latency histogram

### Health Check

`GET /health` returns component-level status:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "application": "healthy",
    "database": "healthy"
  }
}
```

---

## Incident & RCA Workflow

### Lifecycle

```
OPEN → INVESTIGATING → MITIGATED → RESOLVED
```

### RCA Fields

Each incident supports structured root cause analysis:

- **Root Cause** — What caused the incident
- **Remediation** — What was done to fix it
- **Prevention** — What will prevent recurrence

### Severity Levels

`LOW` · `MEDIUM` · `HIGH` · `CRITICAL`

---

## Local Setup

### Prerequisites

- Python 3.12+
- pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/KishanR-dev/servicepulse.git
cd servicepulse

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- API Root: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## Docker

```bash
# Build and run
docker compose up --build

# Run tests in container
docker compose run --rm servicepulse pytest tests/

# View logs
docker compose logs -f
```

The Docker image uses a multi-stage build, runs as non-root, and is configurable via environment variables.

---

## Hugging Face Spaces (Live Demo)

ServicePulse is deployed as a public demo on Hugging Face Spaces:

🔗 **https://huggingface.co/spaces/KishanR-dev/servicepulse**

The deployed instance:
- Runs in `production` mode (failure simulation disabled)
- Uses SQLite for ephemeral data storage
- Resets on container restart (demo data is not persistent)
- Exposes the full API for interactive exploration

> **Note:** This is a portfolio demonstration. The deployed instance does not process real customer requests or connect to production systems.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Python | 3.12+ |
| Database | SQLite (dev/demo) / PostgreSQL (production-ready) |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic 2.11 |
| Testing | pytest 8.4, 89% coverage |
| Linting | Ruff |
| Container | Docker (multi-stage build) |

---

## Known Limitations

1. **SQLite** — Used for development and demo deployment. PostgreSQL migration requires only a `DATABASE_URL` config change.
2. **In-memory metrics** — Metrics reset on restart; not suitable for multi-process deployments.
3. **No authentication** — Appropriate for portfolio context; production would require auth middleware.
4. **Synchronous processing** — Simple request model; async/background jobs are a future enhancement.
5. **Demo data is ephemeral** — SQLite database resets on Hugging Face container restart.

---

## Portfolio Roadmap

ServicePulse is the foundation of a five-project transformation engineering portfolio:

| # | Project | Description | Status |
|---|---|---|---|
| 1 | **servicepulse** | Operations & Incident Management Platform | ✅ Released |
| 2 | servicepulse-ci-cd | CI/CD Pipeline & Quality Automation | 📋 Planned |
| 3 | servicepulse-transformation | Legacy System Transformation | 📋 Planned |
| 4 | servicepulse-requirements | Requirements Engineering & Traceability | 📋 Planned |
| 5 | servicepulse-command-center | Engineering Command Center Dashboard | 📋 Planned |

Each project builds on ServicePulse's stable APIs and architecture.

---

## Documentation

| Document | Purpose |
|---|---|
| [requirements.md](docs/requirements.md) | Functional and non-functional requirements |
| [architecture.md](docs/architecture.md) | System architecture and design |
| [api-design.md](docs/api-design.md) | API endpoint documentation |
| [data-model.md](docs/data-model.md) | Database schema and relationships |
| [testing-strategy.md](docs/testing-strategy.md) | Testing approach and categories |
| [observability.md](docs/observability.md) | Logging, metrics, and monitoring |
| [troubleshooting.md](docs/troubleshooting.md) | Operational procedures |
| [engineering-decisions.md](docs/engineering-decisions.md) | Architectural decision records |
| [traceability-matrix.md](docs/traceability-matrix.md) | Requirement-to-test mapping |

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Co-Authored-By: Claude Code <noreply@anthropic.com>**
