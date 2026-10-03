# ServicePulse — API Design Document

**Version:** 1.0
**Last Updated:** 2025-07-08

---

## 1. API Conventions

- **Base Path:** `/api/v1/`
- **Content Type:** `application/json`
- **Correlation ID:** All requests receive a correlation ID via `X-Correlation-ID` response header. Clients may supply one in the request header.
- **Error Format:** Consistent `{ "error": { "code": ..., "message": ... } }` structure.

---

## 2. Endpoints

### 2.1 Service Requests

#### POST /api/v1/requests

Create a new service request.

**Request Body:**

```json
{
  "customer_id": "CUST-001",
  "request_type": "SERVICE",
  "description": "Unable to access account"
}
```

**Validation:**

| Field | Rules |
|---|---|
| `customer_id` | Required. Pattern: `CUST-\d{3,}` |
| `request_type` | Required. One of: `SERVICE`, `INQUIRY`, `COMPLAINT` |
| `description` | Required. 1–1000 characters |

**Response: 201 Created**

```json
{
  "request_id": "REQ-000001",
  "customer_id": "CUST-001",
  "request_type": "SERVICE",
  "description": "Unable to access account",
  "status": "RECEIVED",
  "created_at": "2025-07-08T10:00:00Z",
  "updated_at": "2025-07-08T10:00:00Z"
}
```

**Errors:**

| Code | HTTP Status | Condition |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Invalid or missing fields |

---

#### GET /api/v1/requests/{request_id}

Retrieve a single request.

**Path Parameters:**

| Parameter | Description |
|---|---|
| `request_id` | Request identifier (e.g., `REQ-000001`) |

**Response: 200 OK**

```json
{
  "request_id": "REQ-000001",
  "customer_id": "CUST-001",
  "request_type": "SERVICE",
  "description": "Unable to access account",
  "status": "PROCESSING",
  "created_at": "2025-07-08T10:00:00Z",
  "updated_at": "2025-07-08T10:01:00Z",
  "processing_started_at": "2025-07-08T10:01:00Z",
  "completed_at": null,
  "failed_at": null,
  "failure_reason": null
}
```

**Errors:**

| Code | HTTP Status | Condition |
|---|---|---|
| `REQUEST_NOT_FOUND` | 404 | ID does not exist |

---

#### GET /api/v1/requests

List service requests with pagination.

**Query Parameters:**

| Parameter | Default | Max | Description |
|---|---|---|---|
| `skip` | 0 | — | Number of records to skip |
| `limit` | 20 | 100 | Number of records to return |

**Response: 200 OK**

```json
{
  "items": [ ... ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

---

#### PATCH /api/v1/requests/{request_id}/status

Update the status of a service request.

**Request Body:**

```json
{
  "status": "PROCESSING"
}
```

**Valid Transitions:**

| From | To |
|---|---|
| `RECEIVED` | `PROCESSING` |
| `PROCESSING` | `COMPLETED` |
| `PROCESSING` | `FAILED` |

**Response: 200 OK** — Updated request object.

**Errors:**

| Code | HTTP Status | Condition |
|---|---|---|
| `REQUEST_NOT_FOUND` | 404 | ID does not exist |
| `INVALID_STATE_TRANSITION` | 409 | Transition not allowed |

---

### 2.2 Incidents

#### POST /api/v1/incidents

Create a new incident.

**Request Body:**

```json
{
  "title": "Elevated processing failures",
  "description": "Processing failure rate exceeded threshold",
  "severity": "HIGH",
  "affected_service": "request_processing",
  "related_request_id": "REQ-000005"
}
```

**Response: 201 Created**

```json
{
  "incident_id": "INC-000001",
  "title": "Elevated processing failures",
  "severity": "HIGH",
  "status": "OPEN",
  "created_at": "2025-07-08T10:05:00Z"
}
```

---

#### GET /api/v1/incidents

List incidents with pagination.

**Query Parameters:** `skip`, `limit` (same as requests).

---

#### GET /api/v1/incidents/{incident_id}

Retrieve a single incident with full details including RCA fields.

---

#### PATCH /api/v1/incidents/{incident_id}

Update incident status, root cause, remediation, or other fields.

**Request Body (partial update):**

```json
{
  "status": "INVESTIGATING",
  "root_cause": "Database connection pool exhaustion under load",
  "remediation": "Increased pool size and added connection timeout"
}
```

**Valid Status Transitions:**

| From | To |
|---|---|
| `OPEN` | `INVESTIGATING` |
| `INVESTIGATING` | `MITIGATED` |
| `MITIGATED` | `RESOLVED` |

---

### 2.3 Health

#### GET /api/v1/health

**Response: 200 OK**

```json
{
  "status": "healthy",
  "timestamp": "2025-07-08T10:00:00Z",
  "components": {
    "application": "healthy",
    "database": "healthy"
  }
}
```

**Response: 503 Service Unavailable** (when degraded)

```json
{
  "status": "unhealthy",
  "timestamp": "2025-07-08T10:00:00Z",
  "components": {
    "application": "healthy",
    "database": "unhealthy"
  }
}
```

---

### 2.4 Metrics

#### GET /api/v1/metrics

Returns Prometheus-compatible text metrics.

**Response: 200 OK** (Content-Type: text/plain)

```
# HELP requests_total Total service requests created
# TYPE requests_total counter
requests_total 42
# HELP requests_by_status Requests by current status
# TYPE requests_by_status gauge
requests_by_status{status="RECEIVED"} 5
requests_by_status{status="PROCESSING"} 3
requests_by_status{status="COMPLETED"} 30
requests_by_status{status="FAILED"} 4
# HELP incidents_open Currently open incidents
# TYPE incidents_open gauge
incidents_open 1
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/requests",status="201"} 42
```

---

## 3. HTTP Status Codes

| Code | Usage |
|---|---|
| 200 | Successful retrieval or update |
| 201 | Successful creation |
| 404 | Resource not found |
| 409 | Conflict (invalid state transition) |
| 422 | Validation error |
| 500 | Unexpected server error |
| 503 | Service unavailable (health check) |

---

## 4. Versioning Strategy

All endpoints are prefixed with `/api/v1/`. Future breaking changes will use `/api/v2/` while maintaining `/api/v1/` for backward compatibility during a transition period.
