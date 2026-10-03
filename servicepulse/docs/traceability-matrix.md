# ServicePulse — Traceability Matrix
**Projects 1–4 — Engineering Traceability & CI/CD Verification**

> Automatically generated from canonical `traceability.json` to prevent drift.

---

## 1. Functional Requirements (FR)

| ID | Title | Components | Implementation Refs | Tests | CI/CD |
|---|---|---|---|---|---|
| **FR-001** | Create Service Request | API Layer, Service Layer | `app/api/routes/requests.py`<br>`app/services/request_service.py` | `tests/api/test_requests.py` | pytest, coverage, ruff, bandit, pip-audit |
| **FR-002** | Validate Input | API Layer | `app/schemas/request.py`<br>`app/api/routes/requests.py` | `tests/unit/test_validation.py` | pytest, coverage, ruff, bandit |
| **FR-003** | Persist Requests | Repository Layer, Database | `app/repositories/request_repository.py`<br>`app/db/models.py` | `tests/integration/test_end_to_end.py` | pytest, coverage, ruff |
| **FR-004** | Retrieve Request | API Layer, Service Layer | `app/api/routes/requests.py`<br>`app/services/request_service.py` | `tests/api/test_requests.py` | pytest, coverage, smoke test |
| **FR-005** | List Requests | API Layer, Service Layer | `app/api/routes/requests.py`<br>`app/services/request_service.py` | `tests/api/test_requests.py` | pytest, coverage, ruff |
| **FR-006** | Update Request Status | Domain Layer, Service Layer | `app/domain/request.py`<br>`app/api/routes/requests.py` | `tests/unit/test_state_machine.py`<br>`tests/regression/test_regression_suite.py` | pytest, coverage |
| **FR-007** | Incident Management | Service Layer, Domain Layer | `app/services/incident_service.py`<br>`app/domain/incident.py` | `tests/api/test_incidents.py`<br>`tests/integration/test_end_to_end.py` | pytest, coverage, smoke test |
| **FR-008** | Health Check | API Layer | `app/api/routes/health.py` | `tests/api/test_health.py` | pytest, smoke test, docker healthcheck |
| **FR-009** | Metrics | Core Infrastructure | `app/core/metrics.py`<br>`app/api/routes/metrics.py` | `tests/api/test_metrics.py` | pytest, coverage |
| **FR-010** | Failure Simulation | Service Layer | `app/services/processing_service.py` | `tests/failure/test_failure_simulation.py`<br>`tests/regression/test_regression_suite.py` | pytest, coverage, bandit |
| **FR-011** | Scalable Identifying Entropy | Service Layer | `app/services/request_service.py`<br>`app/services/incident_service.py` | `tests/api/test_requests.py` | pytest, coverage, ruff, bandit |

---

## 2. Non-Functional Requirements (NFR)

| ID | Title | Components | Implementation Refs | Tests | CI/CD |
|---|---|---|---|---|---|
| **NFR-001** | Structured Logging | Core Infrastructure | `app/core/logging.py` |  | ruff |
| **NFR-002** | Correlation IDs | Core Infrastructure, API Layer | `app/main.py` | `tests/regression/test_regression_suite.py` | pytest, coverage |
| **NFR-006** | Test Isolation | Testing | `tests/conftest.py` | `tests/conftest.py` | pytest |
| **NFR-011** | Production Containerization | Deployment | `Dockerfile` | `scripts/smoke_test.py` | docker build, docker run |
| **NFR-013** | High Concurrency Write Resiliency | Service Layer, Performance | `app/services/request_service.py` | `benchmarks/benchmark_concurrency_after.py` |  |
