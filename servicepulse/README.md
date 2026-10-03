# ServicePulse — Production Operations & Incident Management Platform

**Project 1 of 5 — Transformation Engineering Portfolio**

---

## Project Overview

ServicePulse is a production operations and incident management platform demonstrating the complete engineering lifecycle from requirements through deployment and operational monitoring.

This is the foundational system for a five-project transformation engineering portfolio:

```
                    TRANSFORMATION ENGINEERING
                              │
             ┌────────────────┴────────────────┐
             │                                 │
       REQUIREMENTS                       EXISTING SYSTEM
             │                                 │
             ▼                                 ▼
      PROJECT 4                            PROJECT 3
 Requirements → Design              Legacy Transformation
             │                                 │
             └──────────────┬──────────────────┘
                            ▼
                       PROJECT 1
                    ServicePulse
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
             PROJECT 2             PROJECT 1
             CI/CD + QA          Monitoring/RCA
                 │                     │
                 └──────────┬──────────┘
                            ▼
                       PROJECT 5
                 Engineering Command Center
```

---

## Problem

Building reliable production systems requires:
- Structured request processing with clear lifecycle management
- Incident management with root cause analysis capabilities
- Operational observability through logging and metrics
- Testable, maintainable architecture supporting future evolution

---

## Objectives

This project demonstrates:
- Complete engineering lifecycle (requirements → deployment)
- Clean layered architecture with domain-driven design
- Production-ready API with OpenAPI documentation
- Structured logging and metrics for observability
- Incident management with RCA support
- CI/CD-ready codebase for Project 2
- Performance-analysis foundation for Project 3

---

## Architecture

See [Architecture Documentation](docs/architecture.md)

```
API / Presentation Layer
        ↓
Application / Service Layer
        ↓
Domain Layer
        ↓
Repository / Persistence Layer
        ↓
Database
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Python | 3.12+ |
| Database | SQLite (development) / PostgreSQL (production) |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic 2.11 |
| Testing | pytest 8.4 |
| Code Quality | Ruff |
| Container | Docker / Docker Compose |

---

## Features

### Implemented

| Feature | Status |
|---|---|
| Service request creation and persistence | ✅ |
| Request lifecycle with state machine | ✅ |
| Request retrieval and listing | ✅ |
| Incident management with lifecycle | ✅ |
| Structured JSON logging | ✅ |
| Prometheus-compatible metrics | ✅ |
| Health check endpoint | ✅ |
| Correlation ID tracking | ✅ |
| Centralized error handling | ✅ |
| OpenAPI documentation | ✅ |
| Docker containerization | ✅ |
| Automated tests | ✅ |

### Planned

| Feature | Status |
|---|---|
| PostgreSQL migration | Planned (configuration-ready) |
| Advanced failure simulation | Planned |
| Performance benchmarking | Planned |

---

## Requirements

See [Requirements Documentation](docs/requirements.md)

| ID | Description |
|---|---|
| FR-001 | Create service request |
| FR-002 | Validate input |
| FR-003 | Persist requests |
| FR-004 | Retrieve request |
| FR-005 | List requests |
| FR-006 | Update request status |
| FR-007 | Incident management |
| FR-008 | Health check |
| FR-009 | Metrics |
| FR-010 | Failure simulation (dev only) |

---

## Running Locally

### Prerequisites
- Python 3.12+
- pip

### Installation

```bash
cd servicepulse

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
./scripts/start_dev.sh
```

Or using Docker Compose:

```bash
docker-compose up --build
```

---

## Docker

```bash
# Build
docker-compose build

# Run
docker-compose up

# Run tests
docker-compose run --rm servicepulse pytest tests/

# View logs
docker-compose logs -f
```

---

## Project Status

### Implemented ✅

- Core API endpoints
- Database persistence with SQLite
- Request lifecycle with state machine
- Incident management
- Structured logging
- Metrics endpoint
- Health checks
- Error handling
- Tests (unit, integration, API, failure)
- Docker configuration
- Documentation

### In Progress

- Performance optimization infrastructure

### Planned 📋

- PostgreSQL migration support
- Load testing framework (Project 3)
- CI/CD pipeline (Project 2)

---

## Engineering Decisions

See [Engineering Decisions](docs/engineering-decisions.md)

Key decisions documented:
- Why FastAPI (API-first, async, type hints)
- Why SQLite initially (zero-config, file-based)
- Why layered architecture (separation of concerns)
- Why API versioning (backward compatibility)
- Why structured logging (debugging, analysis)
- Why metrics decoupled from dashboard (flexibility)
- Why modular monolith (time-constrained portfolio)

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

## API Documentation

When running locally, visit:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

---

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/api/
pytest tests/failure/
```

---

## Observability

### Logs

Structured JSON logs with correlation IDs:
```json
{
  "timestamp": "2025-07-08T10:00:00Z",
  "level": "INFO",
  "event": "REQUEST_CREATED",
  "request_id": "REQ-000001",
  "correlation_id": "abc-123"
}
```

### Metrics

Prometheus-compatible format at `/api/v1/metrics`:
- `requests_total` — Total requests created
- `requests_by_status` — Requests by current status
- `http_requests_total` — HTTP request counts
- `http_request_duration` — Request latency

### Health

`/api/v1/health` returns component status:
- Application health
- Database connectivity

---

## Incident Management

### Lifecycle

```
OPEN → INVESTIGATING → MITIGATED → RESOLVED
```

### Severity Levels

- LOW — Minor issue
- MEDIUM — Moderate impact
- HIGH — Significant impact
- CRITICAL — Severe impact

---

## Known Limitations

1. SQLite used for development — PostgreSQL requires config change
2. In-memory metrics storage — not suitable for multi-process
3. No authentication/authorization (portfolio context)
4. No background job processing (simple synchronous model)

---

## Future Projects

### Project 2 — CI/CD + QA Pipeline

This codebase is structured for:
- `make test` — Run all tests
- `make lint` — Linting with Ruff
- `make coverage` — Coverage report
- `make docker-build` — Docker image build
- `make docker-test` — Container tests

### Project 3 — Legacy Transformation

The layered architecture enables:
- Replace `ProcessingService` implementation
- Swap repository implementations
- Measure before/after performance

### Project 4 — Requirements Engineering

Stable requirement IDs (`FR-XXX`) link to:
- Implementation in `app/` directories
- Tests in `tests/` directory
- Traceability matrix in `docs/`

### Project 5 — Command Center

Stable data consumers:
- `/api/v1/metrics` — Dashboard metrics
- `/api/v1/health` — System status
- `/api/v1/incidents` — Active incidents

---

## License

MIT License — See LICENSE file for details.

---

## Maintenance

### Adding a New Dependency

```bash
pip install <package>
pip freeze > servicepulse/requirements.txt
```

### Database Migration (PostgreSQL)

1. Update `DATABASE_URL` environment variable
2. Run application — tables auto-create on startup

---

**Co-Authored-By: Claude Code <noreply@anthropic.com>**
