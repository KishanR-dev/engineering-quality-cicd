#!/usr/bin/env python3
"""ServicePulse — Container and API Smoke Test Suite (Root Invoker)."""

import os
import sys

# Forward directly to servicepulse/scripts/smoke_test.py
TARGET_SCRIPT = os.path.join(
    os.path.dirname(__file__), "..", "servicepulse", "scripts", "smoke_test.py"
)

if __name__ == "__main__":
    import subprocess

    cmd = [sys.executable, TARGET_SCRIPT] + sys.argv[1:]
    sys.exit(subprocess.run(cmd).returncode)
