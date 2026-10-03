"""ServicePulse - Gradio Interface for Interactive Demonstration.

Production-style operations platform demonstrating request lifecycle management
and incident tracking. Powered by FastAPI and SQLite backend.
"""

from __future__ import annotations

import json
import random
from typing import Any

import gradio as gr
from fastapi.testclient import TestClient

# ZeroGPU support check (if deployed on Hugging Face Spaces with ZeroGPU)
try:
    import spaces

    @spaces.GPU
    def _zero_gpu_startup():
        """Satisfy Hugging Face ZeroGPU startup check."""
        return True

    _zero_gpu_startup()
except Exception:
    pass

# Initialize ServicePulse FastAPI application and database
from app.db.database import init_db  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402

init_db()
client = TestClient(fastapi_app)


def _format_json(data: Any) -> str:
    """Helper to pretty-print JSON responses."""
    return json.dumps(data, indent=2, default=str)


def create_request_handler(customer_id: str, request_type: str, description: str) -> str:
    """Handle service request creation."""
    if not customer_id or not customer_id.strip():
        return "Error: Customer ID is required (format: CUST-XXX, e.g., CUST-001)"
    if not description or not description.strip():
        return "Error: Description is required"

    try:
        response = client.post(
            "/api/v1/requests",
            json={
                "customer_id": customer_id.strip(),
                "request_type": request_type,
                "description": description.strip(),
            },
        )
        if response.status_code == 201:
            return _format_json(response.json())
        return f"Status {response.status_code}:\n{_format_json(response.json())}"
    except Exception as e:
        return f"Internal Error: {e}"


def list_requests_handler() -> str:
    """Handle listing service requests."""
    try:
        response = client.get("/api/v1/requests")
        if response.status_code == 200:
            return _format_json(response.json())
        return f"Status {response.status_code}:\n{_format_json(response.json())}"
    except Exception as e:
        return f"Internal Error: {e}"


def get_request_handler(request_id: str) -> str:
    """Handle fetching a single service request by ID."""
    if not request_id or not request_id.strip():
        return "Error: Request ID is required (e.g., REQ-000001)"

    try:
        response = client.get(f"/api/v1/requests/{request_id.strip()}")
        if response.status_code == 200:
            return _format_json(response.json())
        elif response.status_code == 404:
            return f"Not Found (404): Request '{request_id.strip()}' does not exist."
        return f"Status {response.status_code}:\n{_format_json(response.json())}"
    except Exception as e:
        return f"Internal Error: {e}"


def update_status_handler(request_id: str, status: str, failure_reason: str = "") -> str:
    """Handle request lifecycle status updates."""
    if not request_id or not request_id.strip():
        return "Error: Request ID is required"
    if not status:
        return "Error: Target status is required"

    payload: dict[str, Any] = {"status": status}
    if status == "FAILED" and failure_reason and failure_reason.strip():
        payload["failure_reason"] = failure_reason.strip()

    try:
        response = client.patch(
            f"/api/v1/requests/{request_id.strip()}/status",
            json=payload,
        )
        if response.status_code == 200:
            return _format_json(response.json())
        return f"Status {response.status_code}:\n{_format_json(response.json())}"
    except Exception as e:
        return f"Internal Error: {e}"


def create_incident_handler(title: str, description: str, severity: str) -> str:
    """Handle incident creation."""
    if not title or not title.strip():
        return "Error: Incident Title is required"
    if not description or not description.strip():
        return "Error: Incident Description is required"

    try:
        response = client.post(
            "/api/v1/incidents",
            json={
                "title": title.strip(),
                "description": description.strip(),
                "severity": severity,
                "affected_service": "servicepulse_core",
            },
        )
        if response.status_code == 201:
            return _format_json(response.json())
        return f"Status {response.status_code}:\n{_format_json(response.json())}"
    except Exception as e:
        return f"Internal Error: {e}"


def get_health_handler() -> str:
    """Handle health check endpoint."""
    try:
        response = client.get("/health")
        return _format_json(response.json())
    except Exception as e:
        return f"Internal Error: {e}"


def get_metrics_handler() -> str:
    """Handle Prometheus metrics endpoint."""
    try:
        response = client.get("/api/v1/metrics")
        lines = response.text.split("\n")[:40]
        return "\n".join(lines)
    except Exception as e:
        return f"Internal Error: {e}"


def get_requests_table_data() -> list[list[str]]:
    """Fetch request rows for table view."""
    try:
        response = client.get("/api/v1/requests?limit=25")
        if response.status_code == 200:
            items = response.json().get("items", [])
            return [
                [
                    item.get("request_id", ""),
                    item.get("customer_id", ""),
                    item.get("request_type", ""),
                    item.get("status", ""),
                    str(item.get("created_at", "")),
                ]
                for item in items
            ]
        return []
    except Exception:
        return []


def run_automated_workflow() -> str:
    """Execute end-to-end automated demonstration workflow."""
    customer_num = random.randint(100, 999)
    customer_id = f"CUST-{customer_num}"
    test_cases = [
        ("SERVICE", "Automated customer account validation"),
        ("BUG", "Payment retry mechanism validation"),
        ("FEATURE", "Automated export service dispatch"),
        ("SUPPORT", "High-priority onboarding verification"),
    ]
    req_type, desc = random.choice(test_cases)

    steps = [f"=== Starting Automated Demo Workflow for {customer_id} ==="]

    # Step 1: Create Request
    create_resp = client.post(
        "/api/v1/requests",
        json={"customer_id": customer_id, "request_type": req_type, "description": desc},
    )
    if create_resp.status_code != 201:
        steps.append(f"Step 1 Failed: {create_resp.text}")
        return "\n".join(steps)

    req_data = create_resp.json()
    req_id = req_data["request_id"]
    steps.append(f"1. Created Request: {req_id} [Status: {req_data['status']}, Type: {req_type}]")

    # Step 2: Transition to PROCESSING
    proc_resp = client.patch(
        f"/api/v1/requests/{req_id}/status",
        json={"status": "PROCESSING"},
    )
    if proc_resp.status_code != 200:
        steps.append(f"Step 2 Failed: {proc_resp.text}")
        return "\n".join(steps)

    steps.append(f"2. Processing: {req_id} transitioned to PROCESSING")

    # Step 3: Transition to COMPLETED
    comp_resp = client.patch(
        f"/api/v1/requests/{req_id}/status",
        json={"status": "COMPLETED"},
    )
    if comp_resp.status_code != 200:
        steps.append(f"Step 3 Failed: {comp_resp.text}")
        return "\n".join(steps)

    steps.append(f"3. Lifecycle Complete: {req_id} transitioned to COMPLETED successfully!")
    steps.append("=== Workflow Completed Successfully ===")
    return "\n".join(steps)


# Build Gradio UI
with gr.Blocks(title="ServicePulse Demo") as demo:
    gr.Markdown("# ServicePulse Demo")
    gr.Markdown(
        "A production-style operations platform demonstrating request lifecycle management, "
        "incident tracking, and operational observability."
    )

    with gr.Tab("Create Request"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Submit New Request")
                cust_input = gr.Textbox(
                    label="Customer ID",
                    value="CUST-001",
                    placeholder="e.g. CUST-001 or CUST-100",
                )
                type_input = gr.Dropdown(
                    choices=["SERVICE", "BUG", "FEATURE", "SUPPORT"],
                    value="SERVICE",
                    label="Request Type",
                )
                desc_input = gr.Textbox(
                    label="Description",
                    value="User onboarding checklist verification",
                    lines=3,
                )
                create_btn = gr.Button("Create Request", variant="primary")
            with gr.Column():
                create_out = gr.Code(label="API Response", language="json")

        create_btn.click(
            create_request_handler,
            inputs=[cust_input, type_input, desc_input],
            outputs=create_out,
        )

    with gr.Tab("Request Management"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Look Up Request")
                lookup_id = gr.Textbox(label="Request ID", placeholder="e.g. REQ-000001")
                lookup_btn = gr.Button("Get Request Details")

                gr.Markdown("### Update Lifecycle Status")
                status_id = gr.Textbox(label="Request ID for Status Update")
                new_status = gr.Dropdown(
                    choices=["PROCESSING", "COMPLETED", "FAILED"],
                    value="PROCESSING",
                    label="Target Status",
                )
                fail_reason = gr.Textbox(label="Failure Reason (Required for FAILED)")
                update_btn = gr.Button("Update Status", variant="primary")
            with gr.Column():
                lookup_out = gr.Code(label="Lookup Output", language="json")
                update_out = gr.Code(label="Update Output", language="json")

        lookup_btn.click(get_request_handler, inputs=lookup_id, outputs=lookup_out)
        update_btn.click(
            update_status_handler,
            inputs=[status_id, new_status, fail_reason],
            outputs=update_out,
        )

    with gr.Tab("Incidents"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Log New Incident")
                inc_title = gr.Textbox(label="Title", placeholder="e.g. Gateway Latency Spike")
                inc_desc = gr.Textbox(
                    label="Description",
                    placeholder="Describe impact, affected components, and symptoms...",
                    lines=3,
                )
                inc_sev = gr.Dropdown(
                    choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    value="MEDIUM",
                    label="Severity",
                )
                inc_btn = gr.Button("Create Incident", variant="primary")
            with gr.Column():
                inc_out = gr.Code(label="Incident Response", language="json")

        inc_btn.click(
            create_incident_handler,
            inputs=[inc_title, inc_desc, inc_sev],
            outputs=inc_out,
        )

    with gr.Tab("Health & Observability"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Health Check (`/health`)")
                health_btn = gr.Button("Check System Health", variant="primary")
                health_out = gr.Code(label="Health Status", language="json")
            with gr.Column():
                gr.Markdown("### Prometheus Metrics (`/api/v1/metrics`)")
                metrics_btn = gr.Button("Fetch Metrics")
                metrics_out = gr.Textbox(label="Metrics Stream", lines=20)

        health_btn.click(get_health_handler, outputs=health_out)
        metrics_btn.click(get_metrics_handler, outputs=metrics_out)

    with gr.Tab("Automated Test Workflow"):
        gr.Markdown("### Run Automated Lifecycle Demonstration")
        gr.Markdown("Simulates a complete request creation, state transitions, and completion.")
        test_btn = gr.Button("Run Lifecycle Test", variant="secondary")
        test_out = gr.Textbox(label="Workflow Execution Log", lines=8)
        test_btn.click(run_automated_workflow, outputs=test_out)

    with gr.Tab("Live Requests Feed"):
        gr.Markdown("### Current Requests in Database")
        refresh_feed_btn = gr.Button("Refresh Table")
        table_out = gr.Dataframe(
            headers=["Request ID", "Customer ID", "Type", "Status", "Created At"],
            datatype=["str", "str", "str", "str", "str"],
        )
        refresh_feed_btn.click(get_requests_table_data, outputs=table_out)
        demo.load(get_requests_table_data, outputs=table_out)

    gr.Markdown("---")
    gr.Markdown(
        "*ServicePulse v1.0.0 — Production Operations & Incident Management Platform*"
    )

if __name__ == "__main__":
    demo.launch()
