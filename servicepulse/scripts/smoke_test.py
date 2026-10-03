#!/usr/bin/env python3
"""ServicePulse — Container and API Smoke Test Suite.

Validates application readiness and live API contract execution against
a running ServicePulse container or server instance.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def make_request(
    url: str,
    method: str = "GET",
    data: dict | None = None,
    headers: dict | None = None,
    timeout: float = 5.0,
) -> tuple[int, dict | str, dict]:
    """Execute HTTP request using standard library urllib."""
    req_headers = {"User-Agent": "ServicePulse-SmokeTest/1.1.0"}
    if headers:
        req_headers.update(headers)

    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=encoded_data,
        headers=req_headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            status_code = response.getcode()
            resp_headers = dict(response.info())
            raw_body = response.read().decode("utf-8")
            try:
                parsed_body = json.loads(raw_body)
            except json.JSONDecodeError:
                parsed_body = raw_body
            return status_code, parsed_body, resp_headers
    except urllib.error.HTTPError as e:
        status_code = e.code
        resp_headers = dict(e.headers)
        raw_body = e.read().decode("utf-8")
        try:
            parsed_body = json.loads(raw_body)
        except json.JSONDecodeError:
            parsed_body = raw_body
        return status_code, parsed_body, resp_headers


def wait_for_readiness(base_url: str, max_wait: float = 30.0, interval: float = 1.0) -> bool:
    """Poll health endpoint until healthy or timeout."""
    health_url = f"{base_url.rstrip('/')}/health"
    start_time = time.perf_counter()

    print(f"[*] Polling readiness at {health_url} (timeout: {max_wait}s)...")
    while time.perf_counter() - start_time < max_wait:
        try:
            status, body, _ = make_request(health_url, timeout=2.0)
            if status == 200 and isinstance(body, dict) and body.get("status") == "healthy":
                elapsed = time.perf_counter() - start_time
                print(f"[+] Application ready after {elapsed:.2f}s: {body}")
                return True
        except Exception:
            pass
        time.sleep(interval)

    print(f"[-] Application failed to become ready within {max_wait}s")
    return False


def run_smoke_tests(base_url: str) -> int:
    """Execute complete smoke verification checklist."""
    base_url = base_url.rstrip("/")
    passed = 0
    failed = 0

    def assert_check(name: str, condition: bool, details: str = ""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {name} {details}")
        else:
            failed += 1
            print(f"  [FAIL] {name} {details}")

    print("\n" + "=" * 70)
    print(f"SERVICEPULSE SMOKE TEST EXECUTION: {base_url}")
    print("=" * 70)

    # 1. Root Service Info
    print("\n--- [Phase 1] Service Identification ---")
    status, body, _ = make_request(f"{base_url}/")
    assert_check("Root Endpoint Status 200", status == 200, f"(HTTP {status})")
    assert_check(
        "Service Identity Match",
        isinstance(body, dict) and body.get("service") == "ServicePulse",
        f"({body if isinstance(body, dict) else 'non-json'})",
    )

    # 2. Health & Component Check
    print("\n--- [Phase 2] Health & Dependency Check ---")
    status, body, _ = make_request(f"{base_url}/health")
    assert_check("Health Endpoint Status 200", status == 200, f"(HTTP {status})")
    assert_check(
        "Application Component Healthy",
        isinstance(body, dict) and body.get("components", {}).get("application") == "healthy",
    )
    assert_check(
        "Database Component Healthy",
        isinstance(body, dict) and body.get("components", {}).get("database") == "healthy",
    )

    # 3. Metrics Exposure
    print("\n--- [Phase 3] Observability & Metrics Check ---")
    status, body, _ = make_request(f"{base_url}/api/v1/metrics")
    assert_check("Prometheus Metrics Status 200", status == 200, f"(HTTP {status})")
    assert_check(
        "Prometheus Output Contains Metrics",
        isinstance(body, str) and "http_requests_total" in body,
    )

    status, body, _ = make_request(f"{base_url}/api/v1/metrics/json")
    assert_check("JSON Metrics Status 200", status == 200, f"(HTTP {status})")
    assert_check(
        "JSON Metrics Schema Valid",
        isinstance(body, dict) and "counters" in body and "gauges" in body,
    )

    # 4. Service Request Lifecycle
    print("\n--- [Phase 4] Service Request Contract Execution ---")
    req_payload = {
        "customer_id": "CUST-999",
        "request_type": "SERVICE",
        "description": "Smoke test automated request",
    }
    status, body, _ = make_request(f"{base_url}/api/v1/requests", method="POST", data=req_payload)
    assert_check("Create Request Status 201", status == 201, f"(HTTP {status})")
    request_id = body.get("request_id") if isinstance(body, dict) else None
    assert_check("Valid Request ID Generated", bool(request_id and request_id.startswith("REQ-")))

    if request_id:
        status, body, _ = make_request(f"{base_url}/api/v1/requests/{request_id}")
        assert_check("Retrieve Request Status 200", status == 200, f"(HTTP {status})")
        assert_check("Request Initial Status RECEIVED", body.get("status") == "RECEIVED")

        # Update to PROCESSING
        status, body, _ = make_request(
            f"{base_url}/api/v1/requests/{request_id}/status",
            method="PATCH",
            data={"status": "PROCESSING"},
        )
        assert_check("Update to PROCESSING Status 200", status == 200)
        assert_check("Request Status Updated to PROCESSING", body.get("status") == "PROCESSING")

        # Complete Request
        status, body, _ = make_request(
            f"{base_url}/api/v1/requests/{request_id}/status",
            method="PATCH",
            data={"status": "COMPLETED"},
        )
        assert_check("Update to COMPLETED Status 200", status == 200)
        assert_check("Request Status Updated to COMPLETED", body.get("status") == "COMPLETED")

    # 5. Incident Management Lifecycle
    print("\n--- [Phase 5] Operational Incident Contract Execution ---")
    inc_payload = {
        "title": "Smoke Test Incident Simulation",
        "description": "Validation of incident creation and mitigation API",
        "severity": "MEDIUM",
        "affected_service": "smoke_test_runner",
    }
    status, body, _ = make_request(f"{base_url}/api/v1/incidents", method="POST", data=inc_payload)
    assert_check("Create Incident Status 201", status == 201, f"(HTTP {status})")
    incident_id = body.get("incident_id") if isinstance(body, dict) else None
    assert_check(
        "Valid Incident ID Generated", bool(incident_id and incident_id.startswith("INC-"))
    )

    if incident_id:
        status, body, _ = make_request(f"{base_url}/api/v1/incidents/{incident_id}")
        assert_check("Retrieve Incident Status 200", status == 200)
        assert_check("Incident Initial Status OPEN", body.get("status") == "OPEN")

        # Investigate & Mitigate
        status, body, _ = make_request(
            f"{base_url}/api/v1/incidents/{incident_id}",
            method="PATCH",
            data={"status": "INVESTIGATING", "root_cause": "Smoke test execution check"},
        )
        assert_check(
            "Incident Status Updated to INVESTIGATING", body.get("status") == "INVESTIGATING"
        )

    # 6. Error Handling & 404 Contract
    print("\n--- [Phase 6] Error Contract Verification ---")
    status, body, _ = make_request(f"{base_url}/api/v1/requests/REQ-NONEXISTENT-9999")
    assert_check("Not Found Status 404", status == 404, f"(HTTP {status})")
    assert_check(
        "Structured Error Schema Present",
        isinstance(body, dict)
        and "error" in body
        and body["error"].get("code") == "REQUEST_NOT_FOUND",
    )

    print("\n" + "=" * 70)
    print(f"SMOKE TEST SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 70 + "\n")

    return 0 if failed == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="ServicePulse Smoke Test Suite")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("SMOKE_BASE_URL", "http://localhost:8000"),
        help="Base URL of target ServicePulse deployment (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Poll /health endpoint until application is ready before running tests",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Maximum wait timeout in seconds for readiness polling (default: 30.0)",
    )
    args = parser.parse_args()

    if args.wait:
        ready = wait_for_readiness(args.base_url, max_wait=args.timeout)
        if not ready:
            sys.exit(1)

    exit_code = run_smoke_tests(args.base_url)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
