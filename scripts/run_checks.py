#!/usr/bin/env python3
"""ServicePulse — Unified Local Quality & CI/CD Task Runner (Root Invoker)."""

import os
import sys

# Forward directly to servicepulse/scripts/run_checks.py
TARGET_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "servicepulse", "scripts", "run_checks.py"
)

if __name__ == "__main__":
    import subprocess

    cmd = [sys.executable, TARGET_SCRIPT] + sys.argv[1:]
    sys.exit(subprocess.call(cmd))
