# ServicePulse — Traceability Matrix

**Version:** 1.0
**Last Updated:** 2025-07-08**

Maps requirements to implementation components and tests.

---

## Functional Requirements

| ID | Description | Implementation | API / Component | Test |
|---|---|---|---|---|
| FR-001 | Create Service Request | `services/request_service.py:create_request()` | `POST /api/v1/requests` | `tests/api/test_requests.py:test_create_request_success()` |
| FR-002 | Validate Input | `schemas/request.py:CreateRequestSchema` | `POST /api/v1/requests` | `tests/unit/test_validation.py`, `tests/api/test_requests.py:test_create_request_invalid_*` |
| FR-003 | Persist Requests | `repositories/request_repository.py`, `db/models.py` | `services/request_service.py` | `tests/integration/test_end_to_end.py:test_full_lifecycle()` |
| FR-004 | Retrieve Request | `services/request_service.py:get_request()` | `GET /api/v1/requests/{id}` | `tests/api/test_requests.py:test_get_request_success()` |
| FR-005 | List Requests | `services/request_service.py:list_requests()` | `GET /api/v1/requests` | `tests/api/test_requests.py:test_list_requests_with_items()` |
| FR-006 | Update Request Status | `services/request_service.py:update_status()` | `PATCH /api/v1/requests/{id}/status` | `tests/api/test_requests.py:test_update_status_*` |
| FR-007 | Incident Management | `services/incident_service.py`, `domain/incident.py` | `POST/GET/PATCH /api/v1/incidents` | `tests/integration/test_end_to_end.py:test_full_incident_workflow()` |
| FR-008 | Health Check | `api/routes/health.py:health_check()` | `GET /api/v1/health` | `tests/api/test_health.py:test_health_success()` |
| FR-009 | Metrics | `core/metrics.py`, `api/routes/metrics.py` | `GET /api/v1/metrics`, `GET /api/v1/metrics/json` | `tests/api/test_metrics.py:test_metrics_*` |
| FR-010 | Failure Simulation | `services/processing_service.py:_check_simulated_failure()` | Config: `FAILURE_SIMULATION_ENABLED` | `tests/failure/test_failure_simulation.py:test_*` |

---

## Non-Functional Requirements

| ID | Description | Implementation | Test |
|---|---|---|---|
| NFR-001 | Structured Logging | `core/logging.py:StructuredFormatter` | `tests/unit/test_logging.py` (if added) |
| NFR-002 | Correlation IDs | `api/dependencies.py:CorrelationIdMiddleware` | `tests/api/test_requests.py` (verified via headers) |
| NFR-003 | Error Consistency | `core/errors.py:ServicePulseError subclasses` | All error-handling tests |
| NFR-004 | Configuration Externalization | `core/config.py:Settings` | All config-dependent tests |
| NFR-005 | API Versioning | `/api/v1/` prefix in `main.py` | All API tests |
| NFR-006 | Testability | Layered architecture | All test files |
| NFR-007 | Containerization | `Dockerfile`, `docker-compose.yml` | `tests/integration/test_container.py` (if added) |
| NFR-008 | Security Baseline | Input validation, parameterized queries | All validation tests |

---

## Implementation Location Index

| Component | File Path |
|---|---|
| Request Service | `app/services/request_service.py` |
| Incident Service | `app/services/incident_service.py` |
| Processing Service | `app/services/processing_service.py` |
| Request Repository | `app/repositories/request_repository.py` |
| Incident Repository | `app/repositories/incident_repository.py` |
| Request Schema | `app/schemas/request.py` |
| Incident Schema | `app/schemas/incident.py` |
| Request Domain | `app/domain/request.py` |
| Incident Domain | `app/domain/incident.py` |
| Enums | `app/domain/enums.py` |
| Config | `app/core/config.py` |
| Logging | `app/core/logging.py` |
| Errors | `app/core/errors.py` |
| Metrics | `app/core/metrics.py` |
| Database | `app/db/database.py`, `app/db/models.py` |
| Main App | `app/main.py` |

---

## Test Coverage Summary

| Test Category | Files | Status |
|---|---|---|
| Unit | `tests/unit/test_state_machine.py`<br>`tests/unit/test_validation.py` | ✅ Implemented |
| API | `tests/api/test_requests.py`<br>`tests/api/test_health.py`<br>`tests/api/test_metrics.py` | ✅ Implemented |
| Integration | `tests/integration/test_end_to_end.py` | ✅ Implemented |
| Failure | `tests/failure/test_failure_simulation.py` | ✅ Implemented |
| Regression | `tests/regression/` (directory) | 📋 Planned |

---

## Status Legend

- ✅ Implemented
- 📋 Planned
- ⏳ In Progress
