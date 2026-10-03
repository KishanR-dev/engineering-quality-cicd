# Security & Supply-Chain Audit Report: ServicePulse (Project 2: Engineering Quality & CI/CD)

This comprehensive security and supply-chain audit inspects dependencies, secrets management, static application security testing (SAST), GitHub Actions permission architecture, containerization security, and documented baseline controls for the ServicePulse platform.

---

### Finding 1: Transitive Dependency Risk, Lack of Lockfiles, and Missing Supply-Chain Vulnerability Auditing

- **Findings**:
  Direct dependencies in requirements.txt are pinned with exact versions, but transitive sub-dependencies are left unpinned without a deterministic lockfile (such as pip-compile, poetry.lock, or uv.lock). In addition, test, lint, and demo dependencies are bundled together with core runtime dependencies in a single file, and no automated Software Composition Analysis (SCA) / vulnerability scanning tool (e.g., pip-audit, Dependabot) is configured to detect vulnerable third-party packages.

- **Evidence**:
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\requirements.txt`
    Top-level packages are pinned (`fastapi==0.115.12`, `uvicorn[standard]==0.34.3`, `pydantic==2.11.4`, `pydantic-settings==2.9.1`, `sqlalchemy==2.0.41`, `python-dotenv==1.1.0`, `pytest==8.4.1`, `pytest-cov==6.2.1`, `httpx==0.28.1`, `ruff==0.11.12`, `gradio==6.26.0`), but transitive dependencies (`starlette`, `anyio`, `jinja2`, `websockets`, `certifi`, `idna`, `httpcore`, `pydantic-core`) are unpinned.
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\pyproject.toml`
    Standard PEP 621 `[project.dependencies]` and `[project.optional-dependencies]` tables are absent.
  - No `pip-audit` or Dependabot configuration exists in the repository.

- **Severity**: Medium

- **Recommended action**:
  1. Separate dependencies into `requirements.txt` (core runtime), `requirements-dev.txt` (testing/linting: pytest, pytest-cov, httpx, ruff), and `requirements-hf.txt` (demo: gradio).
  2. Integrate `pip-audit` as a supply-chain vulnerability gate in the Project 2 CI pipeline: `pip-audit -r requirements.txt`.
  3. Add a Dependabot configuration file (`.github/dependabot.yml`) for automated pip and GitHub Actions security updates.

- **Reason**:
  Unpinned transitive dependencies can lead to non-deterministic builds and silent ingestion of vulnerable or compromised upstream packages. Separating dev dependencies ensures production container images remain minimal and clean.

- **Whether action is required for Project 2**: Yes (Required as a core CI/CD supply-chain quality gate).

---

### Finding 2: Static Application Security Testing (SAST) Rules Omitted from Linter Configuration

- **Findings**:
  The project uses Ruff for linting, but the Bandit security rule set (`"S"`) is not selected in `pyproject.toml`. Running Ruff with security rules enabled flags unhandled exceptions in startup checks (`S110`), binding to all network interfaces (`S104`), pseudo-random number usage (`S311`), and test assertion statements (`S101`).

- **Evidence**:
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\pyproject.toml`
    Lines 24-26:
    ```toml
    [tool.ruff.lint]
    select = ["E", "F", "I", "N", "W", "UP"]
    ignore = ["E501"]
    ```
  - Executing `ruff check --select S app/` identifies:
    - `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\app\core\config.py`: Line 16 (`S104`: binding to `0.0.0.0`).
  - Executing `ruff check --select S app.py` identifies:
    - `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\app.py`: Line 26 (`S110`: `try-except-pass`), Lines 181, 189 (`S311`: `random.randint`/`random.choice`).
  - Executing `ruff check --select S tests/` identifies `S101` (`assert` statements in pytest test suites).

- **Severity**: Medium

- **Recommended action**:
  1. Add `"S"` to `tool.ruff.lint.select` in `pyproject.toml`.
  2. Configure `tool.ruff.lint.per-file-ignores` in `pyproject.toml` to ignore `S101` in `tests/**/*` and handle intentional demo helpers in `app.py`.
  3. Enforce `ruff check .` with security rules enabled in the Project 2 CI workflow.

- **Reason**:
  Enabling Ruff S-rules provides zero-overhead, sub-second SAST analysis during local development and CI runs, catching security flaws (e.g. insecure deserialization, SQL string interpolation, weak hashing, command injection) before deployment.

- **Whether action is required for Project 2**: Yes (Required for automated SAST quality gating in CI).

---

### Finding 3: Missing CI/CD Workflows and Lack of GitHub Actions Principle of Least Privilege

- **Findings**:
  The repository currently does not contain any GitHub Actions workflows (`.github/workflows/`). When CI/CD is introduced in Project 2, workflows must follow the Principle of Least Privilege to prevent workflow token abuse and supply-chain attacks.

- **Evidence**:
  - Directory: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\.github\workflows` does not exist.
  - Default GitHub Actions execution environment grants broad read/write permissions to `GITHUB_TOKEN` unless top-level restrictions are explicitly declared.

- **Severity**: Medium

- **Recommended action**:
  1. Implement GitHub Actions workflows in `.github/workflows/ci.yml` declaring explicit top-level permissions:
     ```yaml
     permissions:
       contents: read
     ```
  2. Grant granular permissions only at the job level where needed (e.g. `security-events: write` for SARIF results upload, `pull-requests: write` for automated PR metrics).
  3. Pin all GitHub Actions to full commit SHAs with version comments (e.g., `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`) rather than mutable major version tags.
  4. Enforce job-level `timeout-minutes: 10` to avoid runaway CI execution.

- **Reason**:
  Restricting workflow token permissions limits the blast radius of compromised dependencies or malicious pull requests. Pinning actions by immutable commit SHA protects against compromised third-party GitHub Action repositories.

- **Whether action is required for Project 2**: Yes (Mandatory design specification for the Project 2 CI/CD implementation).

---

### Finding 4: Absence of Automated Pre-Commit / CI Secret Scanning Tooling

- **Findings**:
  The repository properly ignores `.env` files via `.gitignore` and provides clean defaults in `.env.example`. A full git commit history inspection confirms no active or historical secrets or private keys were committed. However, no automated secret scanner (e.g., Gitleaks, TruffleHog, or Trivy secret scanning) is configured to detect and block future accidental credential leaks.

- **Evidence**:
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\.gitignore` (correctly lists `.env`).
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\.env.example` (contains only non-sensitive configuration defaults).
  - Git log inspection shows clean commits with no credential leaks.
  - No `.gitleaks.toml`, pre-commit hook configuration, or CI secret scanning workflow exists.

- **Severity**: Low

- **Recommended action**:
  1. Add an automated Gitleaks scan step in the Project 2 GitHub Actions CI workflow using the official open-source action (`gitleaks/gitleaks-action`).
  2. Enable GitHub Secret Scanning and Push Protection in repository settings.

- **Reason**:
  Automated secret scanning provides shift-left detection of credentials, tokens, and API keys before commits are merged or pushed to remote repositories.

- **Whether action is required for Project 2**: Yes (Required as a standard security gate in CI/CD).

---

### Finding 5: Docker Container Security Hardening (Base Image Pinning, Healthchecks, and Non-Root Enforcement)

- **Findings**:
  The primary `Dockerfile` follows strong container security patterns by using a multi-stage build and running as an unprivileged user (`appuser`, UID 1000). However, the Hugging Face Dockerfile (`Dockerfile.hf`) runs as root and retains the `gcc` build tool. Additionally, container images use floating tags (`python:3.12-slim`), the primary `Dockerfile` lacks an inline `HEALTHCHECK` directive (defined only in `docker-compose.yml`), and container image vulnerability scanning is not automated.

- **Evidence**:
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\Dockerfile`
    - Stage 1 / Stage 2 use floating tag `python:3.12-slim`.
    - Line 15, 28: Properly creates and switches to `USER appuser`.
    - Lacks `HEALTHCHECK` instruction.
    - Line 37: Shell form `CMD ["sh", "-c", "..."]` without `exec` can impede standard POSIX signal handling.
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\Dockerfile.hf`
    - Single-stage build; runs as `root` without `USER` directive.
    - Installs and leaves `gcc` in runtime image.
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\docker-compose.yml`
    - Defines container healthcheck on port 8000.

- **Severity**: Low

- **Recommended action**:
  1. Add an open-source Trivy container scan (`aquasecurity/trivy-action`) to the Project 2 CI workflow to scan built Docker images for OS and library CVEs.
  2. Add `USER 1000` to `Dockerfile.hf` for explicit non-root execution.
  3. Add an inline `HEALTHCHECK` command directly to `Dockerfile`.
  4. Pin base images to specific patch versions or SHA256 digests (e.g., `python:3.12.9-slim`).

- **Reason**:
  Non-root execution and removal of build compilers mitigate container escape risks and privilege escalation. Automated image scanning catches known vulnerabilities in base OS distributions.

- **Whether action is required for Project 2**: Partially required (Trivy container scanning in CI is required for Project 2; Dockerfile hardening is recommended).

---

### Finding 6: Reliance on Free, Open-Source Tooling (Zero Paid Tooling Requirement)

- **Findings**:
  The repository is entirely built on open-source foundations. All necessary quality, SAST, SCA, container, and secret scanning requirements can be fulfilled using 100% free and open-source tools or native GitHub free-tier features without requiring paid enterprise licenses or third-party SaaS subscriptions.

- **Evidence**:
  - Current tech stack: FastAPI, Pydantic, SQLAlchemy, pytest, pytest-cov, Ruff, Gradio (all open-source / MIT / Apache 2.0).
  - Recommended security toolchain:
    - Linting & SAST: Ruff (native S-rules / flake8-bandit) and Bandit (Free / Open-Source).
    - Supply-Chain / SCA: `pip-audit` (PyPA official, Free / Open-Source).
    - Secret Scanning: Gitleaks / TruffleHog (Free / Open-Source).
    - Container Scanning: Aqua Security Trivy (Free / Open-Source).
    - CI/CD & Automation: GitHub Actions (Free tier for public repositories) + Dependabot (Free).

- **Severity**: Info

- **Recommended action**:
  1. Standardize Project 2 CI/CD automation exclusively on open-source, vendor-neutral CLI tools that execute locally as well as in GitHub Actions.
  2. Generate standard JUnit test reports, Cobertura coverage reports, and SARIF security outputs using open-source formatters.

- **Reason**:
  Guarantees zero ongoing licensing costs, eliminates vendor lock-in, and ensures anyone cloning the repository can run the entire test and security suite locally.

- **Whether action is required for Project 2**: Yes (Defines the tooling policy and architecture for Project 2).

---

### Finding 7: Default Network Interface Binding (`0.0.0.0`) in Local Configuration

- **Findings**:
  The application configuration defaults `app_host` to `"0.0.0.0"`, binding to all network interfaces by default. While required inside Docker containers, running locally outside of Docker exposes the application to the local area network.

- **Evidence**:
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\app\core\config.py`
    Line 16: `app_host: str = "0.0.0.0"`
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\.env.example`
    Line 8: `APP_HOST=0.0.0.0`

- **Severity**: Low

- **Recommended action**:
  1. Update `app_host` default in `app/core/config.py` to `"127.0.0.1"` for safe local developer workstations.
  2. Override `APP_HOST=0.0.0.0` in Dockerfile, Dockerfile.hf, and docker-compose.yml for container deployments.

- **Reason**:
  Aligns with the principle of secure defaults by ensuring local development servers are only accessible via loopback unless explicitly configured.

- **Whether action is required for Project 2**: No (Architectural polish, optional for Project 2).

---

### Finding 8: Documented Security Safeguards, Failure Gating, and Stack Trace Masking

- **Findings**:
  The codebase exhibits solid baseline defensive design patterns: failure simulation is double-gated to prevent production execution, unhandled exceptions are caught and sanitized to prevent stack trace leakage, input schemas strictly validate patterns and lengths, and database queries use SQLAlchemy parameterized abstractions.

- **Evidence**:
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\app\core\config.py`
    Lines 27-30: `is_failure_simulation_active` requires `app_env == "development"` AND `failure_simulation_enabled == True`.
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\app\core\errors.py`
    Lines 84-93: `unhandled_error_handler` suppresses internal exceptions and returns generic `INTERNAL_ERROR` with correlation IDs.
  - File: `E:\Projects\VSCode\PostOmniroute\WiproGoal\servicepulse\docs\requirements.md`
    NFR-008 explicitly documents the security baseline (no hardcoded secrets, input validation, parameterized queries, stack trace suppression, structured log sanitization).

- **Severity**: Info

- **Recommended action**:
  1. Add automated CI regression tests in Project 2 verifying that `unhandled_error_handler` never leaks stack traces and that failure simulation is blocked in non-development environments.

- **Reason**:
  Continuous validation ensures security invariants and error handling protections remain intact throughout future development.

- **Whether action is required for Project 2**: Yes (Include security baseline assertion tests in CI/CD test suite).

---

### Summary of Audit Action Items for Project 2 (CI/CD Pipeline)

| # | Action Item | Target Component | Tool | Priority for Project 2 |
|---|---|---|---|---|
| 1 | Automated Dependency Vulnerability Audit | Dependencies | `pip-audit` | Required |
| 2 | SAST Linting with Bandit Security Rules | Codebase / Linters | `ruff` (S-rules) | Required |
| 3 | Principle of Least Privilege Permissions | CI Workflows | GitHub Actions `permissions: contents: read` | Required |
| 4 | Automated Secret Detection | Repository History / PRs | `gitleaks` / `trufflehog` | Required |
| 5 | Container Vulnerability Scanning | Docker Images | `trivy` | Required |
| 6 | Automated Dependency Update Checks | Supply Chain | Dependabot (`dependabot.yml`) | Required |
| 7 | Zero Paid Tooling Architecture | Toolchain Policy | 100% Free / Open Source | Required |
| 8 | Non-Root Container Execution | Hugging Face Docker | `Dockerfile.hf` `USER 1000` | Recommended |