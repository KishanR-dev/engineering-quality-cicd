# ServicePulse — Architecture Document

**Version:** 1.0
**Last Updated:** 2025-07-08

---

## 1. System Overview

ServicePulse is a production operations and incident management platform built as a modular monolith. It processes customer service requests through a defined lifecycle, provides operational observability, and supports incident management with root cause analysis.

The system is Project 1 of a five-project Transformation Engineering portfolio and serves as the technical foundation for CI/CD (Project 2), performance optimization (Project 3), requirements traceability (Project 4), and an engineering command center (Project 5).

---

## 2. Architecture Diagram

```mermaid
flowchart TD
    Client["Client / API Consumer"]
    
    subgraph API["API Layer"]
        Routes["Route Handlers"]
        Middleware["Middleware<br/>(Correlation ID, Logging, Metrics)"]
    end
    
    subgraph Service["Service Layer"]
        RequestService["Request Service"]
        IncidentService["Incident Service"]
        ProcessingService["Processing Service"]
    end
    
    subgraph Domain["Domain Layer"]
        StateMachine["State Machine"]
        Enums["Business Enums"]
        Validation["Domain Validation"]
    end
    
    subgraph Persistence["Persistence Layer"]
        RequestRepo["Request Repository"]
        IncidentRepo["Incident Repository"]
    end
    
    subgraph Infrastructure["Infrastructure"]
        DB[("SQLite / PostgreSQL")]
        Logging["Structured Logging"]
        Metrics["Metrics Collector"]
        Config["Configuration"]
    end
    
    Client --> Middleware --> Routes
    Routes --> RequestService
    Routes --> IncidentService
    RequestService --> ProcessingService
    RequestService --> StateMachine
    RequestService --> RequestRepo
    IncidentService --> IncidentRepo
    RequestRepo --> DB
    IncidentRepo --> DB
    RequestService --> Logging
    RequestService --> Metrics
    IncidentService --> Logging
    Middleware --> Logging
    Middleware --> Metrics
```

---

## 3. Component Responsibilities

| Component | Responsibility |
|---|---|
| `api/routes/` | HTTP request/response handling. No business logic. |
| `api/dependencies.py` | FastAPI dependency injection (DB sessions, services). |
| `services/request_service.py` | Request lifecycle orchestration. |
| `services/incident_service.py` | Incident lifecycle orchestration. |
| `services/processing_service.py` | Request processing with failure simulation. |
| `domain/request.py` | Request state machine and domain rules. |
| `domain/incident.py` | Incident state machine and domain rules. |
| `domain/enums.py` | Shared business enumerations. |
| `schemas/` | Pydantic models for API input/output validation. |
| `repositories/` | Database access abstraction. |
| `db/database.py` | SQLAlchemy engine and session management. |
| `db/models.py` | ORM model definitions. |
| `core/config.py` | Centralized configuration from environment. |
| `core/logging.py` | Structured logging setup. |
| `core/errors.py` | Error types and exception handlers. |
| `core/metrics.py` | Application metrics collection. |

---

## 4. Request Lifecycle

```mermaid
stateDiagram-v2
    [*] --> RECEIVED: Create Request
    RECEIVED --> PROCESSING: Start Processing
    PROCESSING --> COMPLETED: Processing Success
    PROCESSING --> FAILED: Processing Failure
    COMPLETED --> [*]
    FAILED --> [*]
```

### Valid Transitions

| From | To | Trigger |
|---|---|---|
| `RECEIVED` | `PROCESSING` | Status update or auto-processing |
| `PROCESSING` | `COMPLETED` | Successful processing |
| `PROCESSING` | `FAILED` | Processing error |

### Invalid Transitions (Rejected)

- `COMPLETED → PROCESSING`
- `FAILED → COMPLETED`
- `RECEIVED → COMPLETED`
- Any transition to `RECEIVED`

---

## 5. Data Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant M as Middleware
    participant R as Route Handler
    participant S as Request Service
    participant P as Processing Service
    participant DB as Database
    participant L as Logger
    participant Met as Metrics

    C->>M: POST /api/v1/requests
    M->>M: Assign Correlation ID
    M->>L: Log request start
    M->>R: Forward request
    R->>R: Validate input (Pydantic)
    R->>S: create_request(data)
    S->>DB: Insert request (RECEIVED)
    S->>L: Log REQUEST_CREATED
    S->>Met: Increment requests_total
    S-->>R: Return request
    R-->>C: 201 Created

    C->>R: PATCH /api/v1/requests/{id}/status
    R->>S: update_status(id, PROCESSING)
    S->>S: Validate state transition
    S->>DB: Update status
    S->>L: Log REQUEST_PROCESSING_STARTED
    S-->>R: Return updated request
```

---

## 6. Error Handling Strategy

All errors are handled through a centralized exception hierarchy:

```
ServicePulseError (base)
├── ValidationError
├── NotFoundError
├── InvalidStateTransitionError
├── DatabaseError
├── ProcessingError
└── FailureSimulationError
```

FastAPI exception handlers translate these into consistent JSON responses:

```json
{
  "error": {
    "code": "REQUEST_NOT_FOUND",
    "message": "The requested service request was not found.",
    "correlation_id": "abc-123"
  }
}
```

Internal errors never expose stack traces or implementation details to API consumers.

---

## 7. Observability

| Mechanism | Implementation |
|---|---|
| **Structured Logging** | JSON-formatted logs with correlation IDs, event types, durations |
| **Metrics** | In-process counters/histograms exposed via `/api/v1/metrics` |
| **Health Checks** | `/api/v1/health` with component-level status |
| **Correlation IDs** | Auto-generated or client-supplied via `X-Correlation-ID` header |

See [Observability Document](observability.md) for details.

---

## 8. Persistence

- **ORM:** SQLAlchemy 2.0 with declarative models
- **Initial DB:** SQLite (file-based, zero-config)
- **Target DB:** PostgreSQL (no business logic changes required)
- **Pattern:** Repository pattern isolating SQL from service logic
- **Migrations:** Alembic-ready structure (migrations directory present)

The repository interface is designed so swapping SQLite → PostgreSQL requires only a `DATABASE_URL` change.

---

## 9. Deployment Model

```mermaid
flowchart LR
    subgraph Development
        Local["Python + uvicorn"]
    end
    
    subgraph Container
        Docker["Docker"]
        Compose["Docker Compose"]
    end
    
    subgraph Future
        CI["GitHub Actions<br/>(Project 2)"]
    end
    
    Local --> Docker
    Docker --> Compose
    Compose --> CI
```

---

## 10. Future Extension Points

| Extension | Mechanism |
|---|---|
| **PostgreSQL migration** | Change `DATABASE_URL` environment variable |
| **CI/CD pipeline** (Project 2) | GitHub Actions consuming `make` / script commands |
| **Performance optimization** (Project 3) | Replace `ProcessingService` internals; repository is isolated |
| **Requirements traceability** (Project 4) | Stable requirement IDs (`FR-XXX`) linked to tests and code |
| **Command Center dashboard** (Project 5) | Consume `/api/v1/metrics`, `/api/v1/health`, `/api/v1/incidents` |

---

## 11. Architectural Decisions

See [Engineering Decisions](engineering-decisions.md) for ADR-style records of key decisions including:

- ADR-001: Why FastAPI
- ADR-002: Why SQLite initially
- ADR-003: Why layered architecture
- ADR-004: Why API versioning
- ADR-005: Why structured logging
- ADR-006: Why metrics are decoupled from dashboard
- ADR-007: Why modular monolith
