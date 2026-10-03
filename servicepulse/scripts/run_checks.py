#!/usr/bin/env python3
"""ServicePulse — Unified Local Quality & CI/CD Task Runner.

Allows developers and automated agents to locally reproduce all CI/CD
stages with identical flags, thresholds, and exit codes.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))


def run_command(
    cmd: list[str] | str,
    cwd: str = PROJECT_ROOT,
    env: dict | None = None,
    shell: bool = False,
) -> int:
    """Run a shell or subprocess command and stream output."""
    full_env = os.environ.copy()
    full_env["PYTHONIOENCODING"] = "utf-8"
    if env:
        full_env.update(env)

    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    print(f"\n[EXEC] {cmd_str} (cwd: {cwd})")
    start = time.perf_counter()
    result = subprocess.run(cmd, cwd=cwd, env=full_env, shell=shell)
    elapsed = time.perf_counter() - start
    status = "SUCCESS" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"[{status}] in {elapsed:.2f}s")
    return result.returncode


def stage_lint() -> int:
    print("\n" + "=" * 60 + "\nSTAGE: STATIC QUALITY & LINTING (Ruff)\n" + "=" * 60)
    ret1 = run_command(["ruff", "check", "."])
    if ret1 != 0:
        return ret1
    ret2 = run_command(["ruff", "format", "--check", "."])
    return ret2


def stage_security() -> int:
    print("\n" + "=" * 60 + "\nSTAGE: SECURITY & SUPPLY CHAIN AUDIT\n" + "=" * 60)
    print("\n[*] Running dependency vulnerability audit (pip-audit)...")
    ret1 = run_command(
        [sys.executable, "-m", "pip_audit", "-r", "requirements.txt"],
        cwd=PROJECT_ROOT,
    )
    if ret1 != 0:
        return ret1

    print("\n[*] Running static application security testing (bandit)...")
    ret2 = run_command(
        [sys.executable, "-m", "bandit", "-r", "app"],
        cwd=PROJECT_ROOT,
    )
    return ret2


def stage_tests() -> int:
    print("\n" + "=" * 60 + "\nSTAGE: TEST EXECUTION (pytest)\n" + "=" * 60)
    return run_command([sys.executable, "-m", "pytest", "tests/"], cwd=PROJECT_ROOT)


def stage_coverage() -> int:
    print("\n" + "=" * 60 + "\nSTAGE: COVERAGE VALIDATION (pytest-cov >= 85%)\n" + "=" * 60)
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-fail-under=85",
        ],
        cwd=PROJECT_ROOT,
    )


def stage_docker_build() -> int:
    print("\n" + "=" * 60 + "\nSTAGE: DOCKER IMAGE BUILD\n" + "=" * 60)
    return run_command(
        ["docker", "build", "-t", "servicepulse:local", "."],
        cwd=PROJECT_ROOT,
    )


def stage_docker_smoke() -> int:
    print("\n" + "=" * 60 + "\nSTAGE: DOCKER CONTAINER SMOKE TESTING\n" + "=" * 60)
    # 1. Build
    build_code = stage_docker_build()
    if build_code != 0:
        return build_code

    container_name = f"servicepulse-smoke-{int(time.time())}"
    port = 8000

    print(f"\n[*] Starting container {container_name} on port {port}...")
    run_cmd = [
        "docker",
        "run",
        "-d",
        "--name",
        container_name,
        "-p",
        f"{port}:8000",
        "-e",
        "APP_ENV=development",
        "-e",
        "PORT=8000",
        "servicepulse:local",
    ]
    start_code = subprocess.run(run_cmd).returncode
    if start_code != 0:
        print("[-] Failed to start Docker container")
        return start_code

    smoke_code = 1
    try:
        smoke_script = os.path.join(PROJECT_ROOT, "scripts", "smoke_test.py")
        smoke_cmd = [
            sys.executable,
            smoke_script,
            "--base-url",
            f"http://localhost:{port}",
            "--wait",
            "--timeout",
            "30",
        ]
        smoke_code = run_command(smoke_cmd, cwd=PROJECT_ROOT)
    finally:
        print(f"\n[*] Tearing down container {container_name}...")
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    return smoke_code


def stage_all() -> int:
    stages = [
        ("Lint & Format", stage_lint),
        ("Security Audit", stage_security),
        ("Tests & Coverage", stage_coverage),
        ("Docker Smoke Test", stage_docker_smoke),
    ]

    for name, stage_fn in stages:
        code = stage_fn()
        if code != 0:
            print(f"\n[FATAL] Pipeline halted. Stage failed: {name} (exit code {code})")
            return code

    print("\n" + "=" * 60)
    print("ALL QUALITY GATES PASSED (100% SUCCESS)")
    print("=" * 60 + "\n")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="ServicePulse Quality & CI/CD Local Runner")
    parser.add_argument(
        "stage",
        choices=["lint", "security", "test", "coverage", "docker-build", "docker-smoke", "all"],
        help="Pipeline stage to execute locally",
    )
    args = parser.parse_args()

    stage_map = {
        "lint": stage_lint,
        "security": stage_security,
        "test": stage_tests,
        "coverage": stage_coverage,
        "docker-build": stage_docker_build,
        "docker-smoke": stage_docker_smoke,
        "all": stage_all,
    }

    exit_code = stage_map[args.stage]()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
