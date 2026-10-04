# Project 2 — Engineering Quality & CI/CD

> Part of the [Transformation Engineering Portfolio](https://github.com/KishanR-dev/servicepulse). This standalone repository hosts the remote delivery layer, CI/CD pipelines, and configuration metrics for the ServicePulse backend system. 

[![Tests](https://img.shields.io/badge/tests-78%20passed-green.svg)](#testing--quality-gates)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#testing--quality-gates)
[![Ruff](https://img.shields.io/badge/linting-ruff-orange.svg)](https://docs.astral.sh/ruff/)
[![Security: Bandit & pip-audit](https://img.shields.io/badge/security-passed-brightgreen.svg)](#security--supply-chain)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](#containerization--smoke-testing)

🔗 **[Live API Documentation & Demo](https://engineering-quality-cicd-dhlf.onrender.com/docs)**

> **Note:** The live demonstration is hosted on Render's free tier to showcase the CD capabilities of this layer. Spin-up may take 30-50 seconds from sleep. 

---

## Why a Separate Repository?

This project (`engineering-quality-cicd`) acts as the dedicated CI/CD and Quality pipeline layer for the overall ServicePulse portfolio. While [Projects 1, 3, 4, and 5 exist in the primary ServicePulse repository](https://github.com/KishanR-dev/servicepulse), this repository specifically isolates the delivery engineering tasks:
- Containerization (Multi-stage unprivileged Docker builds)
- Security checks (Bandit and Pip-Audit)
- Continuous Integration Gates (Pytest + coverage verification)
- Continuous Deployment configuration (`render.yaml`)

## Core Capabilities

| Capability | Implementation |
|---|---|
| **Testing & Quality** | 78 deterministic tests across Unit, API, Integration, Failure, and Regression |
| **Code Coverage** | **94.65%** statement coverage enforced by CI quality gates (`--cov-fail-under=85`) |
| **Static Analysis** | Ruff linting and formatting enforced with zero tolerance |
| **Security & SAST** | Automated `pip-audit` dependency scanning and `bandit` AST checks |
| **Containerization** | Multi-stage Docker build with non-root user and automated HTTP smoke test suite |
| **CI/CD Automation** | GitHub Actions workflows for PRs, branch pushes, and versioned releases |

## CI/CD Pipeline Architecture

The Continuous Integration pipeline enforces a strict four-stage quality gate on every Pull Request and commit to `master`:

1. **Static Quality**: `ruff check` & `ruff format --check`
2. **Security**: `pip-audit` and `bandit -r app`
3. **Test Gates**: `pytest tests/` and `pytest-cov >= 85%` capability verification
4. **Smoke Validate**: `docker build`, ephemeral run, and HTTP readiness verification via `smoke_test.py`

## Portfolio Hub

For details regarding domain implementation, concurrency optimization (Project 3), traceability (Project 4), and the Command Center (Project 5), please reference the overarching **[ServicePulse Portfolio Hub](https://github.com/KishanR-dev/servicepulse)**.
