# ServicePulse — Production Operations & Engineering Quality Platform

**Projects 1 & 2 of 5 — Transformation Engineering Portfolio**

> A production-style operations and automated engineering quality platform demonstrating the complete software delivery lifecycle: requirements → domain modeling → implementation → multi-layered testing → static analysis → SAST security audit → containerization → CI/CD automation → live smoke validation.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/tests-78%20passed-green.svg)](#testing--quality-gates)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#testing--quality-gates)
[![Ruff](https://img.shields.io/badge/linting-ruff-orange.svg)](https://docs.astral.sh/ruff/)
[![Security: Bandit & pip-audit](https://img.shields.io/badge/security-passed-brightgreen.svg)](#security--supply-chain)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](#containerization--smoke-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🔗 **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/KishanR-dev/engineering-quality-cicd)** · 📖 **[API Documentation](/api/v1/docs)**

> **Note:** Hugging Face Spaces uses a Gradio interactive interface for public demonstration. Full OpenAPI/Swagger documentation is available when running locally at `/api/v1/docs` or `/docs`.

---

## Portfolio Architecture & Roadmap

ServicePulse forms the foundation of a five-project Transformation Engineering portfolio:

```text
                 ServicePulse (P1)
         Production Operations & Incidents
                      │
                      ▼
               Project 2 (CI/CD)
           Engineering Quality & Gates
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   Project 3 (P3)  Project 4 (P4)  Project 5 (P5)
   Transformation   Requirements    Command Center
```

| # | Project | Focus | Status |
|---|---|---|---|
| **1** | **ServicePulse Core** | Operations & Incident Management Platform | ✅ Released (`v1.0.0`) |
| **2** | **Engineering Quality & CI/CD** | Automated QA, Security, Docker, Quality Gates, Release | ✅ Released (`v1.1.0`) |
| **3** | Transformation Engineering | Legacy transformation + measurable performance optimization | 📋 Planned |
| **4** | Requirements Engineering | Traceability Case Study (Reqs → Design → Code → Tests) | 📋 Planned |
| **5** | Transformation Command Center | Unified Engineering & Operations Dashboard | 📋 Planned |

---

## Core Capabilities

| Capability | Implementation |
|---|---|
| **Service Request Lifecycle** | Create → Process → Complete / Fail with state machine validation |
| **Incident Management** | Open → Investigate → Mitigate → Resolve with root cause analysis (RCA) |
| **Layered Architecture** | Clean separation: API → Service → Domain → Repository → Database |
| **Testing & Quality** | 78 deterministic tests across Unit, API, Integration, Failure, and Regression |
| **Code Coverage** | **94.65%** statement coverage enforced by CI quality gates (`--cov-fail-under=85`) |
| **Static Analysis** | Ruff linting and formatting enforced with zero tolerance |
| **Security & SAST** | Automated `pip-audit` dependency scanning and `bandit` AST vulnerability checks |
| **Container & Smoke Testing** | Multi-stage Docker build with non-root user and automated HTTP smoke test suite |
| **CI/CD Automation** | GitHub Actions workflows for PRs, branch pushes, and versioned releases |
| **Observability** | Structured JSON logging with correlation IDs + Prometheus-compatible metrics |
| **Failure Simulation** | Development-only, double-gated controlled fault injection |

---

## CI/CD Pipeline Architecture

The Continuous Integration & Delivery pipeline enforces a strict four-stage quality gate on every Pull Request and commit to `master`:

```text
┌────────────────┐
│  Code Change   │
└───────┬────────┘
        ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 1: Static Quality & Linting                       │
│ • ruff check .               (Linting & code standards) │
│ • ruff format --check .      (Deterministic formatting) │
└───────┬─────────────────────────────────────────────────┘
        ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 2: Security & Supply Chain Audit                  │
│ • pip-audit -r requirements.txt (Vulnerability scan)    │
│ • bandit -r app -ll -ii         (SAST security analysis)│
└───────┬─────────────────────────────────────────────────┘
        ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 3: Automated Testing & Coverage Gate              │
│ • pytest tests/              (78 tests: Unit, API, Reg) │
│ • pytest-cov >= 85%          (Enforced coverage gate)   │
└───────┬─────────────────────────────────────────────────┘
        ▼
┌─────────────────────────────────────────────────────────┐
│ Stage 4: Container Build & Live Smoke Test              │
│ • docker build               (Multi-stage build)        │
│ • docker run                 (Ephemeral container)      │
│ • smoke_test.py --wait       (Full HTTP API validation) │
└───────┬─────────────────────────────────────────────────┘
        ▼
┌────────────────┐
│  Release Gate  │ (Tag v*.*.* triggers wheel packaging)
└────────────────┘
```

---

## Local Quality Commands (Reproduce CI Locally)

ServicePulse provides a unified task runner to locally execute any or all CI stages with identical parameters:

```bash
# Run all quality gates in sequence (full CI reproduction)
python scripts/run_checks.py all

# Run specific stages individually:
python scripts/run_checks.py lint          # Ruff lint & format
python scripts/run_checks.py security      # pip-audit + bandit
python scripts/run_checks.py test          # pytest test suite
python scripts/run_checks.py coverage      # pytest with coverage enforcement
python scripts/run_checks.py docker-build  # Build local Docker image
python scripts/run_checks.py docker-smoke  # Build, run container, and execute smoke test
```

---

## Testing & Quality Gates

The test suite contains **78 tests** organized into five categorized layers:

| Marker / Category | Directory | Purpose | Count |
|---|---|---|---|
| `@pytest.mark.unit` | `tests/unit/` | State machines, schema validations, processing mechanics | 35 |
| `@pytest.mark.api` | `tests/api/` | Health, Metrics, Service Requests, and Incidents endpoints | 26 |
| `@pytest.mark.integration` | `tests/integration/` | End-to-end request and incident lifecycles | 3 |
| `@pytest.mark.failure` | `tests/failure/` | Gated fault injection, failure handling, invalid transitions | 4 |
| `@pytest.mark.regression` | `tests/regression/` | State immutability, simulation gating, correlation propagation | 10 |
| **Total** | | | **78** |

### Test Isolation
Tests utilize an in-memory SQLite database with SQLAlchemy `StaticPool` and automated per-test schema creation/teardown. All in-memory metrics counters are strictly reset before each test via autouse fixtures, guaranteeing 100% determinism and zero state leakage across test cases.

---

## Security & Supply Chain

1. **Dependency Vulnerability Auditing (`pip-audit`):** Scans all dependencies against the PyPI Advisory Database.
2. **Static Application Security Testing (`bandit`):** AST-based security linting to catch common vulnerabilities (CWE).
3. **Environment Double-Gating:** Failure simulation is physically disabled in production mode even if flags are set.
4. **Least-Privilege Execution:** Docker containers run under a dedicated unprivileged `appuser` (UID 1000).
5. **No Secret Leakage:** Strict `.gitignore` and `.env.example` templates; zero credentials stored in repository.

---

## Containerization & Smoke Testing

### Dockerfile Highlights
- **Multi-Stage Build:** Builder stage installs dependencies; production stage copies only pre-built wheels and packages.
- **Unprivileged User:** Dedicated `appuser` without root privileges.
- **Native Healthcheck:** Built-in `HEALTHCHECK` polling `/health` via Python standard library `urllib`.

### Automated Smoke Test Suite (`scripts/smoke_test.py`)
Validates a running instance across 6 critical operational phases:
1. **Service Identity:** Root `/` returns service metadata and status.
2. **Health Verification:** `/health` reports application and database components as `healthy`.
3. **Observability:** `/api/v1/metrics` exposes Prometheus exposition format and JSON metrics.
4. **Request Lifecycle:** Creates request, updates status through `PROCESSING` to `COMPLETED`.
5. **Incident Lifecycle:** Creates incident, transitions through investigation and mitigation.
6. **Error Contracts:** Verifies structured 404 error responses.

---

## Controlled Failure Demonstration

As part of Project 2 engineering verification, a controlled defect scenario was executed and documented:
- **Scenario:** Inadvertent regression allowing transition from terminal `COMPLETED` state.
- **Detection:** Caught automatically at CI test gate with zero false positives.
- **Remediation:** Fix applied to domain logic + permanent regression test added.
- **Documentation:** See [Controlled CI Failure Demo](servicepulse/docs/controlled-ci-failure-demo.md).

---

## Project Structure

```text
servicepulse/
├── .github/
│   ├── dependabot.yml              # Automated dependency updates
│   └── workflows/
│       ├── ci.yml                  # Main CI quality gate pipeline
│       └── release.yml             # Release validation & packaging
├── app/
│   ├── api/
│   │   └── routes/                 # FastAPI router endpoints (health, requests, incidents, metrics)
│   ├── core/                       # Config, logging, metrics, error handling
│   ├── db/                         # Database engine, session maker, ORM models
│   ├── domain/                     # Pure business logic, state machines, enums
│   ├── repositories/               # Data access layer
│   ├── schemas/                    # Pydantic request/response validation schemas
│   ├── services/                   # Application orchestration services
│   └── main.py                     # FastAPI application factory & lifespan
├── docs/                           # Architecture, requirements, audits & traceability docs
├── scripts/
│   ├── run_checks.py               # Local unified quality runner
│   └── smoke_test.py               # Standalone HTTP smoke test suite
├── tests/                          # 78 automated tests (Unit, API, Integration, Failure, Regression)
├── Dockerfile                      # Multi-stage production container definition
├── pyproject.toml                  # Project configuration, Ruff, pytest, coverage settings
├── requirements.txt                # Core runtime dependencies
├── requirements-dev.txt            # Testing, linting, security tools
└── requirements-hf.txt             # Hugging Face Spaces Gradio requirements
```

---

## Getting Started

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/KishanR-dev/engineering-quality-cicd.git
cd servicepulse

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install development dependencies
pip install -r servicepulse/requirements-dev.txt

# 4. Run local validation suite
python scripts/run_checks.py all

# 5. Start development server
cd servicepulse && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Traceability & Documentation

| Document | Purpose |
|---|---|
| [requirements.md](servicepulse/docs/requirements.md) | Functional and non-functional requirements |
| [architecture.md](servicepulse/docs/architecture.md) | System architecture, layers, and data flow |
| [api-design.md](servicepulse/docs/api-design.md) | REST API endpoints and data contracts |
| [testing-strategy.md](servicepulse/docs/testing-strategy.md) | Test hierarchy, isolation, and coverage policy |
| [controlled-ci-failure-demo.md](servicepulse/docs/controlled-ci-failure-demo.md) | Controlled failure & RCA demonstration |
| [traceability-matrix.md](servicepulse/docs/traceability-matrix.md) | Requirement → Implementation → Test → CI mapping |
| [observability.md](servicepulse/docs/observability.md) | Structured logging and Prometheus metrics |
| [troubleshooting.md](servicepulse/docs/troubleshooting.md) | Operational triage procedures |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
