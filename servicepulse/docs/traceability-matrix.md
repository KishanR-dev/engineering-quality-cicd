# ServicePulse — Traceability Matrix
**Projects 1 & 2 — Engineering Traceability & CI/CD Verification**

> Maps requirements to implementation components, automated tests, and CI/CD quality gate enforcement.

---

## 1. Functional Requirements (FR)

| ID | Requirement Description | Implementation Component | API Route | Automated Test | CI/CD Quality Gate |
|---|---|---|---|---|---|
| **FR-001** | Create Service Request | `app/services/request_service.py:create_request()` | `POST /api/v1/requests` | `tests/api/test_requests.py::TestCreateRequest::test_create_request_success` | CI Stage 3 (pytest) |
| **FR-002** | Schema & Format Validation | `app/schemas/request.py:CreateRequestSchema` | `POST /api/v1/requests` | `tests/unit/test_validation.py::TestCreateRequestValidation` | CI Stage 3 (pytest) |
| **FR-003** | Persistent Request Storage | `app/repositories/request_repository.py`, `app/db/models.py` | Internal Data Access | `tests/integration/test_end_to_end.py::TestRequestLifecycle` | CI Stage 3 (pytest) |
| **FR-004** | Retrieve Single Request | `app/services/request_service.py:get_request()` | `GET /api/v1/requests/{id}` | `tests/api/test_requests.py::TestGetRequest::test_get_request_success` | CI Stage 3 (pytest) + Smoke Test Phase 4 |
| **FR-005** | List Requests (Paginated) | `app/services/request_service.py:list_requests()` | `GET /api/v1/requests` | `tests/api/test_requests.py::TestListRequests::test_list_requests_with_items` | CI Stage 3 (pytest) |
| **FR-006** | Request Lifecycle State Machine | `app/domain/request.py:validate_request_transition()` | `PATCH /api/v1/requests/{id}/status` | `tests/unit/test_state_machine.py::TestRequestStateMachine`, `tests/regression/test_regression_suite.py::TestTerminalStateImmutabilityRegression` | CI Stage 3 (pytest) + Smoke Test Phase 4 |
| **FR-007** | Incident Management Lifecycle | `app/services/incident_service.py`, `app/domain/incident.py` | `POST /api/v1/incidents`, `PATCH /api/v1/incidents/{id}` | `tests/api/test_incidents.py`, `tests/integration/test_end_to_end.py::TestIncidentLifecycle` | CI Stage 3 (pytest) + Smoke Test Phase 5 |
| **FR-008** | Component Health Monitoring | `app/api/routes/health.py:health_check()` | `GET /health` | `tests/api/test_health.py::TestHealthCheck` | CI Stage 3 (pytest) + Docker Healthcheck + Smoke Phase 2 |
| **FR-009** | Observability & Metrics | `app/core/metrics.py:MetricsCollector` | `GET /api/v1/metrics`, `GET /api/v1/metrics/json` | `tests/api/test_metrics.py::TestMetrics` | CI Stage 3 (pytest) + Smoke Phase 3 |
| **FR-010** | Double-Gated Failure Simulation | `app/services/processing_service.py:_check_simulated_failure()` | Internal Processing Guard | `tests/failure/test_failure_simulation.py`, `tests/regression/test_regression_suite.py::TestFailureSimulationGatingRegression` | CI Stage 3 (pytest) |

---

## 2. Non-Functional Requirements (NFR)

| ID | Quality Requirement | Implementation Mechanism | Verification / Test | CI/CD Quality Gate |
|---|---|---|---|---|
| **NFR-001** | Structured JSON Logging | `app/core/logging.py:StructuredFormatter` | Verified across all API interactions | CI Stage 1 (Ruff) + Local Runner |
| **NFR-002** | Correlation ID Propagation | `app/main.py:CorrelationIdMiddleware` | `tests/regression/test_regression_suite.py::TestMiddlewareCorrelationRegression` | CI Stage 3 (pytest) |
| **NFR-003** | Error Standardization | `app/core/errors.py:register_error_handlers()` | `tests/api/test_requests.py:test_get_request_not_found`, `tests/api/test_incidents.py:test_get_incident_not_found` | CI Stage 3 (pytest) + Smoke Phase 6 |
| **NFR-004** | Configuration Externalization | `app/core/config.py:Settings` (Pydantic BaseSettings) | Environment variable overrides in tests & Docker | CI Stage 3 (pytest) + Docker Smoke |
| **NFR-005** | API Versioning | `/api/v1/` prefix in `app/main.py` | All API endpoint test paths | CI Stage 3 (pytest) |
| **NFR-006** | Test Isolation & Speed | `tests/conftest.py` (In-memory SQLite + StaticPool) | 78 tests execute in < 1.5s with zero state leakage | CI Stage 3 (pytest) |
| **NFR-007** | Minimum Code Coverage (>= 85%) | `pyproject.toml` (`[tool.coverage.report]`) | Enforced statement coverage (currently 94.65%) | CI Stage 3 (`--cov-fail-under=85`) |
| **NFR-008** | Static Code Quality | Ruff linting and formatting configuration | `ruff check .` and `ruff format --check .` | CI Stage 1 (Ruff) |
| **NFR-009** | Vulnerability Auditing | Dependency scanning with `pip-audit` | Scans `requirements.txt` against PyPI database | CI Stage 2 (pip-audit) |
| **NFR-010** | Static Application Security (SAST) | AST vulnerability analysis with `bandit` | Scans `app/` with `-ll -ii` (zero tolerance) | CI Stage 2 (Bandit) |
| **NFR-011** | Production Containerization | Multi-stage `Dockerfile`, unprivileged `appuser` | Docker build and container run in CI pipeline | CI Stage 4 (Docker Build) |
| **NFR-012** | Live Container Smoke Validation | `scripts/smoke_test.py` (6-phase HTTP contract suite) | Automated execution against live container | CI Stage 4 (Smoke Test) |

---

## 3. Architecture & Code Map

| Domain / Layer | Primary Files | Traceability & Responsibilities |
|---|---|---|
| **API Routing** | `app/api/routes/health.py`<br>`app/api/routes/requests.py`<br>`app/api/routes/incidents.py`<br>`app/api/routes/metrics.py` | HTTP contract, validation schemas, status codes, OpenAPI metadata |
| **Application Services** | `app/services/request_service.py`<br>`app/services/incident_service.py`<br>`app/services/processing_service.py` | Business logic orchestration, state transitions, domain events, logging |
| **Domain Logic** | `app/domain/request.py`<br>`app/domain/incident.py`<br>`app/domain/enums.py` | Pure state machines, transition invariants, severity definitions |
| **Persistence** | `app/repositories/request_repository.py`<br>`app/repositories/incident_repository.py`<br>`app/db/database.py`<br>`app/db/models.py` | SQLAlchemy ORM queries, database session lifecycle, schema metadata |
| **Core Infrastructure** | `app/core/config.py`<br>`app/core/logging.py`<br>`app/core/metrics.py`<br>`app/core/errors.py`<br>`app/main.py` | Pydantic settings, JSON logging, metrics singleton, error hierarchy, lifespan |
