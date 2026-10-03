# ServicePulse — Troubleshooting Guide

**Version:** 1.0
**Last Updated:** 2025-07-08

---

## 1. API Failure

### Symptoms

- HTTP 500 responses
- Requests not processed
- No response from endpoints

### Investigation Steps

```
1. Check health endpoint: curl http://localhost:8000/api/v1/health
2. Get correlation ID from request/response headers
3. Search logs: grep "<correlation_id>" app.log
4. Check database connectivity
5. Review error logs for stack trace
```

### Common Causes

| Cause | Resolution |
|---|---|
| Database connection lost | Restart server, verify DATABASE_URL |
| Invalid JSON in request | Verify request body format |
| Invalid state transition | Review request lifecycle documentation |
| Unhandled exception | Check logs for traceback |

---

## 2. Database Failure

### Symptoms

- Health check returns 503
- `database` component shows unhealthy
- Database errors in logs

### Investigation Steps

```
1. Check database file exists (SQLite): ls data/servicepulse.db
2. Verify DATABASE_URL environment variable
3. Test database connection: python -c "from app.db.database import engine; engine.connect()"
4. Check database logs for errors
```

### Common Causes

| Cause | Resolution |
|---|---|
| File permissions | Fix ownership on data directory |
| Corrupted database | Delete and restart (development only) |
| Wrong DATABASE_URL | Update .env file |

---

## 3. Processing Failure

### Symptoms

- Requests stuck in PROCESSING
- High `requests_failed_total` metric
- `REQUEST_FAILED` events in logs

### Investigation Steps

```
1. List failed requests: grep "REQUEST_FAILED" logs
2. Check failure_reason field in database
3. Review processing service logs
4. Verify no infinite loops in processing code
```

### Recovery

```bash
# Query failed requests
sqlite3 data/servicepulse.db "SELECT request_id, failure_reason FROM service_requests WHERE status='FAILED';"

# Manually transition to COMPLETED (only if appropriate)
sqlite3 data/servicepulse.db "UPDATE service_requests SET status='COMPLETED' WHERE request_id='REQ-XXXXXX';"
```

---

## 4. High Error Rate

### Symptoms

- Elevated 4xx/5xx responses
- Metrics show `http_requests_total{status=~"5.."}`
- Users report failures

### Investigation Steps

```
1. Check health endpoint
2. Review /api/v1/metrics/json for patterns
3. Search logs for ERROR level entries
4. Correlate with deployment events
```

### Quick Checks

| Check | Command |
|---|---|
| Current errors | `grep "ERROR" logs/app.log \| wc -l` |
| Failed requests | `grep "REQUEST_FAILED" logs/app.log \| wc -l` |
| Invalid state transitions | `grep "INVALID_STATE_TRANSITION" logs/app.log \| wc -l` |

---

## 5. Incident Investigation

### Procedure

```
1. Identify incident ID from /api/v1/incidents
2. Get incident details: curl http://localhost:8000/api/v1/incidents/INC-XXXXXX
3. Review related_request_id if present
4. Search logs for correlation IDs
5. Check metrics at time of detection
```

### Documentation Template

```
Incident: INC-XXXXXX
Timestamp: 2025-07-08T10:00:00Z

Symptoms:
- [Describe what users observed]

Evidence:
- Error logs: [list relevant log entries]
- Metrics: [describe anomaly]

Investigation:
- [Describe debugging steps taken]

Root Cause:
- [Specific technical cause]

Remediation:
- [Steps taken to resolve]

Prevention:
- [Changes to prevent recurrence]

Regression Test:
- [Test to verify fix]
```

---

## 6. Correlation ID Search

### Command Line

```bash
# Search for all entries with a specific correlation ID
grep "abc-123" logs/app.log

# Find all error entries in a time window
grep "ERROR" logs/app.log \| grep "2025-07-08T10:"
```

### Log Format for Search

Each log entry contains:
```json
{"correlation_id": "abc-123", "request_id": "REQ-000001", "event": "..."}
```

---

## 7. Development Server Issues

### Server won't start

```
1. Check Python version: python --version (need 3.12+)
2. Verify dependencies: pip install -r requirements.txt
3. Check port is free: lsof -i :8000
4. Review startup logs for import errors
```

### API docs not available

```
1. Verify app is running: curl http://localhost:8000/api/v1/health
2. Check path: /api/v1/docs (not /docs)
3. Verify APP_ENV=development
```

---

## 8. Testing Issues

### Tests fail with database errors

```bash
# Clean test database
rm -f test_servicepulse.db
pytest tests/
```

### No test output

```bash
pytest -v -s tests/
```

### Coverage not updating

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov
open htmlcov/index.html
```

---

## 9. Docker Issues

### Container won't start

```bash
# Check logs
docker-compose logs servicepulse

# Common fixes:
# - Verify .env file exists
# - Check port 8000 is not in use
# - Ensure data directory exists
```

### Database persistence

```bash
# Database is stored in ./data directory
ls -la data/

# To reset (development only):
docker-compose down -v
rm -rf data/
docker-compose up
```

---

## 10. Common Error Codes

| Code | Message | Resolution |
|---|---|---|
| VALIDATION_ERROR | Invalid input | Check request body format |
| REQUEST_NOT_FOUND | Request ID not found | Verify ID format (REQ-XXXXXX) |
| INCIDENT_NOT_FOUND | Incident ID not found | Verify ID format (INC-XXXXXX) |
| INVALID_STATE_TRANSITION | Cannot change status | Check lifecycle diagram |
| DATABASE_ERROR | Database operation failed | Check database connectivity |
| SIMULATED_FAILURE | Development simulation | Expected in test mode |
