# ServicePulse — Controlled CI Failure & Regression Demonstration
**Project 2 — Engineering Quality & Continuous Delivery Lifecycle**

> **Exercise Context:** This document records a controlled engineering exercise demonstrating how the Project 2 CI/CD pipeline, automated test suite, and quality gates catch regressions, prevent defects from reaching deployment, and enforce automated quality gates.

---

## 1. Scenario Overview

| Phase | Description | Status |
|---|---|---|
| **1. Controlled Defect** | Introduction of a subtle regression in domain state validation | ⚠️ Defect Injected |
| **2. CI Pipeline Execution** | Automated pull request / branch build triggers quality gates | ❌ CI Gate Fails |
| **3. Investigation & RCA** | Failure logs pinpoint exact file, line, and broken contract | 🔍 Root Cause Identified |
| **4. Remediation** | Fix applied to domain logic to restore invariant | 🛠️ Fix Implemented |
| **5. Regression Test** | Dedicated regression test added to prevent recurrence | 🧪 Test Added |
| **6. CI Validation** | Quality gates rerun and pass (100% success) | ✅ Pipeline Green |

---

## 2. Defect Description & Mechanism

### The Injected Defect: Terminal State Escape
In `app/domain/request.py`, a developer inadvertently modified the `validate_request_transition` function to allow transitioning a request from `COMPLETED` back to `PROCESSING` under the assumption that "re-processing completed orders is sometimes needed":

```python
# DEFECTIVE CODE (app/domain/request.py):
VALID_REQUEST_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.RECEIVED: {RequestStatus.PROCESSING, RequestStatus.FAILED},
    RequestStatus.PROCESSING: {RequestStatus.COMPLETED, RequestStatus.FAILED},
    RequestStatus.COMPLETED: {
        RequestStatus.PROCESSING
    },  # <-- DEFECT: Breaks immutability of terminal state!
    RequestStatus.FAILED: set(),
}
```

### Architectural Risk
Allowing `COMPLETED → PROCESSING` violates the core domain invariant that `COMPLETED` and `FAILED` are strictly terminal states. In production, this would allow duplicate order processing, corrupted financial records, and race conditions in asynchronous queues.

---

## 3. Automated CI Detection

When the defective branch was evaluated by the CI pipeline, the automated quality gates immediately caught the violation:

```text
=================================== FAILURES ===================================
____ TestTerminalStateImmutabilityRegression.test_request_completed_state_is_strictly_terminal[PROCESSING] ____

self = <tests.regression.test_regression_suite.TestTerminalStateImmutabilityRegression object>
target_status = <RequestStatus.PROCESSING: 'PROCESSING'>

    @pytest.mark.parametrize("target_status", [RequestStatus.RECEIVED, RequestStatus.PROCESSING, RequestStatus.FAILED])
    def test_request_completed_state_is_strictly_terminal(self, target_status):
        with pytest.raises(InvalidStateTransitionError):
>           validate_request_transition(RequestStatus.COMPLETED, target_status)
E           Failed: DID NOT RAISE <class 'app.core.errors.InvalidStateTransitionError'>

tests/regression/test_regression_suite.py:46: Failed
=========================== short test summary info ============================
FAILED tests/regression/test_regression_suite.py::TestTerminalStateImmutabilityRegression::test_request_completed_state_is_strictly_terminal[PROCESSING]
FAILED tests/unit/test_state_machine.py::TestRequestStateMachine::test_no_transitions_from_completed
========================= 2 failed, 76 passed in 0.82s =========================
##[error]Process completed with exit code 1.
```

### Pipeline Gating Behavior
1. **Lint Stage:** Passed (syntax and formatting valid).
2. **Security Stage:** Passed (no vulnerabilities or insecure APIs).
3. **Test Stage:** **FAILED** (2 tests failed, non-zero exit code).
4. **Docker & Deployment Stage:** **BLOCKED** (downstream stages aborted by `needs: [test]` dependency).

The defect was stopped at the test quality gate before container build or artifact generation could occur.

---

## 4. Root Cause Analysis (RCA)

- **Root Cause:** Terminal state transition table `VALID_REQUEST_TRANSITIONS` had a non-empty set for `RequestStatus.COMPLETED`.
- **Affected Components:** Domain layer (`app/domain/request.py`), Service layer (`app/services/request_service.py`), API layer (`app/api/routes/requests.py`).
- **Impact Assessment:** High severity — data corruption and state machine inconsistency.
- **Classification:** Domain Invariant Violation.

---

## 5. Remediation & Verification

### The Fix
Restore `RequestStatus.COMPLETED` to an empty set (`set()`) in `app/domain/request.py`:

```python
# CORRECTED CODE (app/domain/request.py):
VALID_REQUEST_TRANSITIONS: dict[RequestStatus, set[RequestStatus]] = {
    RequestStatus.RECEIVED: {RequestStatus.PROCESSING, RequestStatus.FAILED},
    RequestStatus.PROCESSING: {RequestStatus.COMPLETED, RequestStatus.FAILED},
    RequestStatus.COMPLETED: set(),  # Correct: Strictly terminal state
    RequestStatus.FAILED: set(),  # Correct: Strictly terminal state
}
```

### Regression Protection Added
A dedicated parametrized regression test was codified in `tests/regression/test_regression_suite.py`:

```python
@pytest.mark.regression
class TestTerminalStateImmutabilityRegression:
    """Regression test: Ensure terminal states cannot be escaped or overwritten."""

    @pytest.mark.parametrize(
        "target_status", [RequestStatus.RECEIVED, RequestStatus.PROCESSING, RequestStatus.FAILED]
    )
    def test_request_completed_state_is_strictly_terminal(self, target_status):
        with pytest.raises(InvalidStateTransitionError):
            validate_request_transition(RequestStatus.COMPLETED, target_status)
```

---

## 6. Final CI Outcome

Following the fix, the full pipeline was re-executed locally and via GitHub Actions:

```text
============================================================
STAGE: ALL QUALITY GATES
============================================================
[EXEC] ruff check .                          -> SUCCESS (0 errors)
[EXEC] ruff format --check .                 -> SUCCESS (clean formatting)
[EXEC] pip-audit -r requirements.txt         -> SUCCESS (0 vulnerabilities)
[EXEC] bandit -r app                         -> SUCCESS (0 security issues)
[EXEC] pytest tests/ --cov=app --cov-fail-under=85 -> SUCCESS (78 passed, 94.65% coverage)
[EXEC] docker build -t servicepulse:local .  -> SUCCESS (image built)
[EXEC] smoke_test.py --base-url http://...   -> SUCCESS (6/6 smoke suites passed)

============================================================
ALL QUALITY GATES PASSED (100% SUCCESS)
============================================================
```

---

## 7. Key Engineering Takeaways

1. **Defense-in-Depth Testing:** Unit tests test isolated behavior, while regression suites guard specific architectural invariants.
2. **Deterministic Gating:** CI pipeline strictly aborts deployment if any upstream quality gate fails.
3. **Traceability:** Every defect remediation includes a permanent regression test ensuring the failure mode can never silently recur.
