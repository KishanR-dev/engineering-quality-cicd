# ServicePulse — Testing Strategy

**Version:** 1.0
**Last Updated:** 2025-07-08

---

## 1. Testing Philosophy

Test coverage should provide confidence in:
1. Correct business logic (state transitions, validation)
2. API contract adherence (endpoints return expected responses)
3. Error handling (invalid input, failures, edge cases)
4. Regression prevention (no accidental breakage)

---

## 2. Test Categories

### Unit Tests (`tests/unit/`)

**Purpose:** Test individual components in isolation

**Coverage:**
- State machine validation
- Domain validation logic
- Error class instantiation
- Schema validation

**Naming Convention:** `test_<module>_<functionality>.py`

**Example:**
```python
def test_valid_received_to_processing():
    validate_request_transition(RequestStatus.RECEIVED, RequestStatus.PROCESSING)

def test_invalid_state_transition_raises_error():
    with pytest.raises(InvalidStateTransitionError):
        validate_request_transition(RequestStatus.COMPLETED, RequestStatus.PROCESSING)
```

---

### Integration Tests (`tests/integration/`)

**Purpose:** Test component interactions and data flow

**Coverage:**
- Database CRUD operations
- Service layer orchestration
- Repository pattern
- Full request/incident lifecycle

**Naming Convention:** `test_<scenario>.py`

**Example:**
```python
def test_full_request_lifecycle(client, sample_request_data):
    # Create → Retrieve → Update → Complete
    # Verify timestamps and status transitions
```

---

### API Tests (`tests/api/`)

**Purpose:** Verify HTTP layer behavior

**Coverage:**
- Endpoint responses
- Status codes (200, 201, 400, 404, 409, 422)
- Request/response schemas
- Error response formats
- Pagination

**Naming Convention:** `test_<resource>_<operation>.py`

**Example:**
```python
def test_create_request_success(client, sample_request_data):
    response = client.post("/api/v1/requests", json=sample_request_data)
    assert response.status_code == 201
```

---

### Failure Tests (`tests/failure/`)

**Purpose:** Verify failure scenarios and recovery

**Coverage:**
- Invalid state transitions
- Database errors
- Validation failures
- Controlled failure simulation

**Naming Convention:** `test_<failure_type>.py`

**Example:**
```python
def test_cannot_complete_from_received(client, sample_request_data):
    response = client.patch(
        f"/api/v1/requests/{request_id}/status",
        json={"status": "COMPLETED"},
    )
    assert response.status_code == 409
```

---

### Regression Tests (`tests/regression/`)

**Purpose:** Long-running tests for stable functionality

**Coverage:**
- Critical user workflows
- Performance baselines
- Data integrity checks

**Naming Convention:** `test_regression_<feature>.py`

---

## 3. Test Fixtures

### Conftest Fixtures

| Fixture | Scope | Description |
|---|---|---|
| `db_session` | function | Fresh database for each test |
| `client` | function | TestClient with DB override |
| `sample_request_data` | function | Valid request payload |
| `sample_incident_data` | function | Valid incident payload |

### Factory Pattern

For complex test data, use factory functions:

```python
def make_request(db, status=RequestStatus.RECEIVED):
    model = ServiceRequestModel(
        request_id=f"REQ-{random.randint(1, 1000000):06d}",
        customer_id="CUST-999",
        request_type="SERVICE",
        description="Test",
        status=status.value,
    )
    db.add(model)
    db.commit()
    return model
```

---

## 4. Test Data Strategy

- **Deterministic:** Same inputs → same outputs
- **Isolated:** Tests don't share state
- **Clean:** Database cleaned after each test
- **Safe:** No external dependencies (APIs, files)

---

## 5. Running Tests

```bash
# All tests
pytest -v

# Specific category
pytest tests/unit/
pytest tests/api/test_requests.py

# With coverage
pytest --cov=app --cov-report=term-missing

# Single test
pytest -k "test_create_request"
```

---

## 6. Test Coverage Targets

| Component | Target |
|---|---|
| State machine | 100% |
| Schema validation | 100% |
| API endpoints | 90% |
| Service layer | 80% |
| Repositories | 80% |

---

## 7. CI/CD Integration

Project 2 will integrate these commands:

```bash
# Linting
ruff check app/

# Type checking (mypy)
mypy app/

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v

# Full suite with coverage
pytest --cov=app --cov-report=xml:coverage.xml
```
