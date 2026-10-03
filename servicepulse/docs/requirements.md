# ServicePulse — Requirements Specification

**Version:** 1.0
**Status:** Implemented
**Last Updated:** 2025-07-08

---

## 1. Overview

ServicePulse is a production operations and incident management platform designed to demonstrate the complete engineering lifecycle from requirements through deployment and operational reporting.

---

## 2. Functional Requirements

### FR-001 — Create Service Request

The system shall allow a client to create a service request with:
- `customer_id` (required, format: `CUST-XXX`)
- `request_type` (required, one of: `SERVICE`, `INQUIRY`, `COMPLAINT`)
- `description` (required, 1–1000 characters)

The system shall return a unique request ID (format: `REQ-XXXXXX`) and the initial status `RECEIVED`.

**Status:** Implemented
**API:** `POST /api/v1/requests`
**Tests:** `test_create_request`, `test_create_request_returns_id`

---

### FR-002 — Validate Input

The system shall validate all incoming service request payloads:
- Required fields must be present
- `customer_id` must match pattern `CUST-\d{3,}`
- `request_type` must be an accepted enum value
- `description` must be between 1 and 1000 characters
- Malformed JSON must be rejected

Invalid requests must return HTTP 422 with a structured error response.

**Status:** Implemented
**API:** `POST /api/v1/requests`
**Tests:** `test_create_request_invalid_customer_id`, `test_create_request_missing_fields`, `test_create_request_invalid_type`

---

### FR-003 — Persist Requests

The system shall persist service requests in a relational database. The persistence layer is abstracted through a repository pattern to support future migration from SQLite to PostgreSQL.

**Status:** Implemented
**Component:** `repositories/request_repository.py`
**Tests:** `test_request_persistence`

---

### FR-004 — Retrieve Request

The system shall allow retrieval of a single service request by its ID.

**Status:** Implemented
**API:** `GET /api/v1/requests/{request_id}`
**Tests:** `test_get_request`, `test_get_request_not_found`

---

### FR-005 — List Requests

The system shall allow listing service requests with pagination support.

Query parameters:
- `skip` (default: 0)
- `limit` (default: 20, max: 100)

**Status:** Implemented
**API:** `GET /api/v1/requests`
**Tests:** `test_list_requests`, `test_list_requests_pagination`

---

### FR-006 — Update Request Status

The system shall allow controlled status transitions following the defined state machine.

Valid transitions:
- `RECEIVED → PROCESSING`
- `PROCESSING → COMPLETED`
- `PROCESSING → FAILED`

Invalid transitions shall be rejected with HTTP 409.

**Status:** Implemented
**API:** `PATCH /api/v1/requests/{request_id}/status`
**Tests:** `test_status_transition`, `test_invalid_status_transition`

---

### FR-007 — Incident Management

The system shall support a complete incident lifecycle:
- Create incidents (manual or automated from failure threshold)
- Update incident status through valid transitions
- Record root cause analysis
- Document remediation

**Status:** Implemented
**API:** `POST /api/v1/incidents`, `GET /api/v1/incidents`, `PATCH /api/v1/incidents/{incident_id}`
**Tests:** `test_create_incident`, `test_incident_lifecycle`

---

### FR-008 — Health Check

The system shall expose a health endpoint reporting status of the application and its dependencies.

**Status:** Implemented
**API:** `GET /api/v1/health`
**Tests:** `test_health_check`

---

### FR-009 — Metrics

The system shall expose Prometheus-compatible application metrics.

**Status:** Implemented
**API:** `GET /api/v1/metrics`
**Tests:** `test_metrics_endpoint`

---

### FR-010 — Failure Simulation

The system shall provide a development-only mechanism to simulate failures for testing and demonstration purposes. Disabled by default; requires `ENVIRONMENT=development` and `FAILURE_SIMULATION_ENABLED=true`.

**Status:** Implemented
**Configuration:** Environment variables
**Tests:** `test_failure_simulation`

---

## 3. Non-Functional Requirements

### NFR-001 — Structured Logging

All application events shall be logged in structured JSON format with correlation IDs, timestamps, log level, and contextual information.

**Status:** Implemented

---

### NFR-002 — Correlation IDs

Every API request shall be assigned a unique correlation ID. If the client supplies `X-Correlation-ID`, the system shall use it. Otherwise, one is generated.

**Status:** Implemented

---

### NFR-003 — Error Consistency

All error responses shall use a consistent JSON structure with `error.code`, `error.message`, and optional contextual fields.

**Status:** Implemented

---

### NFR-004 — Configuration Externalization

All environment-specific settings shall be configurable via environment variables with sensible defaults.

**Status:** Implemented

---

### NFR-005 — API Versioning

All endpoints are served under `/api/v1/` to support future API evolution.

**Status:** Implemented

---

### NFR-006 — Testability

The architecture must support unit, integration, API, failure, and regression testing without external dependencies.

**Status:** Implemented

---

### NFR-007 — Containerization

The application shall be runnable via Docker and Docker Compose.

**Status:** Implemented

---

### NFR-008 — Security Baseline

- No secrets committed to version control
- Input validation on all endpoints
- No SQL injection (parameterized queries via SQLAlchemy)
- No stack traces in API responses
- No sensitive data in logs

**Status:** Implemented

---

## 4. Traceability

See [Traceability Matrix](traceability-matrix.md) for requirement-to-implementation mapping.

### FR-011 — Scalable Identifying Entropy (Transformation)

The system shall independently generate request and incident IDs using a high entropy shorter UUID strategy avoiding sequential database querying.
Ids must remain capped within legacy string constraints (e.g., 20 characters).

**Status:** Implemented (Project 3 Transformation)
**API:** `POST /api/v1/requests`, `POST /api/v1/incidents`
**Tests:** `test_uuid_generation`, `test_request_creation_stress`

---

### NFR-013 — High Concurrency Write Resiliency

The system must sustain simultaneous request writes globally under high concurrency without Database locking constraints or transaction conflicts (e.g., `sqlite3.IntegrityError`). Specifically, a benchmark of 50 concurrent requests must execute with 0% failure rate.

**Status:** Implemented (Project 3 Transformation)
**Validation:** `benchmarks/benchmark_concurrency_after.py`

---
