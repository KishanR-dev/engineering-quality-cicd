# ServicePulse — Observability Document

**Version:** 1.0
**Last Updated:** 2025-07-08

---

## 1. Logging

### Format

All logs are emitted as single-line JSON objects:

```json
{
  "timestamp": "2025-07-08T10:00:00.000000+00:00",
  "level": "INFO",
  "logger": "servicepulse.request_service",
  "message": "Service request created",
  "event": "REQUEST_CREATED",
  "request_id": "REQ-000001",
  "correlation_id": "abc-123",
  "customer_id": "CUST-001"
}
```

### Event Types

| Event | Level | Description |
|---|---|---|
| `REQUEST_CREATED` | INFO | New service request received |
| `REQUEST_PROCESSING_STARTED` | INFO | Request entered PROCESSING status |
| `REQUEST_COMPLETED` | INFO | Request processing succeeded |
| `REQUEST_FAILED` | ERROR | Request processing failed |
| `INCIDENT_CREATED` | INFO | New incident created |
| `INCIDENT_RESOLVED` | INFO | Incident marked resolved |
| `DATABASE_ERROR` | ERROR | Database operation failed |
| `SIMULATED_FAILURE` | WARNING | Development failure injection |
| `HTTP_REQUEST_START` | DEBUG | Incoming request received |
| `HTTP_REQUEST_COMPLETE` | INFO | Request completed |

### Log Levels

| Level | Usage |
|---|---|
| DEBUG | Detailed flow information |
| INFO | Normal operations |
| WARNING | Unexpected but handled |
| ERROR | Operational failures |
| CRITICAL | System unavailable |

---

## 2. Metrics

### Counter Metrics

| Name | Labels | Description |
|---|---|---|
| `requests_total` | — | Total requests created |
| `requests_success_total` | — | Requests completed successfully |
| `requests_failed_total` | — | Requests that failed |
| `http_requests_total` | method, endpoint, status | HTTP request counts |
| `incidents_total` | — | Total incidents created |

### Gauge Metrics

| Name | Labels | Description |
|---|---|---|
| `requests_by_status` | status | Requests in each state |
| `incidents_by_status` | status | Incidents in each state |
| `incidents_open` | — | Currently open incidents |

### Histogram Metrics

| Name | Labels | Description |
|---|---|---|
| `request_processing_duration` | — | Request processing time (ms) |
| `http_request_duration` | endpoint | HTTP request latency (ms) |
| `request_latency` | — | Total request latency (ms) |

### Prometheus Output Example

```
# HELP requests_total Total service requests created
# TYPE requests_total counter
requests_total 42

# HELP requests_by_status Requests by current status
# TYPE requests_by_status gauge
requests_by_status{status="RECEIVED"} 5
requests_by_status{status="PROCESSING"} 3
requests_by_status{status="COMPLETED"} 30

# HELP request_processing_duration Request processing duration
# TYPE request_processing_duration summary
request_processing_duration_count 100
request_processing_duration_sum 1250.50
request_processing_duration_avg 12.50
```

---

## 3. Health Checks

### Endpoint

`GET /api/v1/health`

### Response Structure

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-07-08T10:00:00.000000+00:00",
  "components": {
    "application": "healthy",
    "database": "healthy"
  }
}
```

### Status Codes

| Code | Condition |
|---|---|
| 200 | All components healthy |
| 503 | One or more components unhealthy |

### Component Check Logic

1. **Application** — Always healthy if server is running
2. **Database** — Verified by executing `SELECT 1`

---

## 4. Correlation IDs

### Generation

- If client supplies `X-Correlation-ID`, use it
- Otherwise, generate UUID (first 8 chars for brevity)

### Propagation

- Added to response header: `X-Correlation-ID: abc-123`
- Included in all log entries for the request

### Usage in RCA

When investigating an incident:
1. Identify error time window
2. Search logs for correlation IDs
3. Trace request flow through all components

---

## 5. Operational Questions

### Can answer with current implementation:

| Question | Data Source |
|---|---|
| How many requests are being processed? | `requests_total`, `requests_by_status` |
| How many succeed vs fail? | `requests_success_total`, `requests_failed_total` |
| How long do requests take? | `request_processing_duration` histogram |
| What endpoints are slow? | `http_request_duration` histogram |
| How many incidents are open? | `incidents_open` gauge, `/api/v1/incidents` |
| What errors occurred? | `error` field in logs |

### Requires future enhancement:

| Question | Enhancement Needed |
|---|---|
| Root cause of failure X? | Link logs to incidents, store RCA |
| What's the error rate? | Calculate from counters |
| How many incidents per day? | Time-series queries |

---

## 6. Failure Investigation Procedure

### Step 1: Identify the incident

```
1. Check /api/v1/health
2. Query /api/v1/metrics/json for error rates
3. Review open incidents
```

### Step 2: Find relevant logs

```
1. Note error timestamp
2. Search logs for event types: REQUEST_FAILED, DATABASE_ERROR
3. Extract correlation_id from error log
```

### Step 3: Trace the request

```
1. Use correlation_id to find all related log entries
2. Build timeline: START → PROCESSING → FAILED
3. Identify the last successful operation
```

### Step 4: Document findings

```
1. Record root cause
2. Document remediation steps
3. Create prevention measures
4. Update incident record
```
