"""Gradio interface for Hugging Face Spaces deployment.

This module provides a demo interface that exercises ServicePulse functionality
through its REST API. The interface uses the internal FastAPI app for all logic.
"""

import json
import random
import sqlite3
from pathlib import Path

import gradio as gr
import httpx

# Configuration for Spaces
BASE_URL = "http://127.0.0.1:7860"
DATA_DIR = Path("/app/data")
DB_PATH = DATA_DIR / "servicepulse.db"


def get_db_connection():
    """Get database connection for the demo."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_requests_list():
    """Get list of requests for the demo table."""
    if not DB_PATH.exists():
        return []
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "SELECT request_id, customer_id, request_type, status, created_at FROM service_requests ORDER BY created_at DESC LIMIT 20"
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def create_request(customer_id: str, request_type: str, description: str) -> dict:
    """Create a request using the FastAPI app."""
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{BASE_URL}/api/v1/requests",
            json={
                "customer_id": customer_id,
                "request_type": request_type,
                "description": description,
            },
        )
        response.raise_for_status()
        return response.json()


def list_requests() -> list:
    """List requests."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/api/v1/requests")
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])


def get_request(request_id: str) -> dict:
    """Get a single request."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/api/v1/requests/{request_id}")
        response.raise_for_status()
        return response.json()


def update_request_status(request_id: str, status: str, failure_reason: str = None) -> dict:
    """Update request status."""
    payload = {"status": status}
    if failure_reason:
        payload["failure_reason"] = failure_reason
    with httpx.Client(timeout=10.0) as client:
        response = client.patch(
            f"{BASE_URL}/api/v1/requests/{request_id}/status",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def create_incident(title: str, description: str, severity: str) -> dict:
    """Create an incident."""
    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            f"{BASE_URL}/api/v1/incidents",
            json={
                "title": title,
                "description": description,
                "severity": severity,
                "affected_service": "servicepulse_demo",
            },
        )
        response.raise_for_status()
        return response.json()


def get_health() -> dict:
    """Get health status."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/health")
        response.raise_for_status()
        return response.json()


def get_metrics() -> dict:
    """Get metrics."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/api/v1/metrics")
        response.raise_for_status()
        return {"text": response.text}


# Demo functions for Gradio interface
def demo_create_request(customer_id: str, request_type: str, description: str):
    """Handle request creation."""
    if not customer_id or not description:
        return "Error: Please provide customer ID and description"
    try:
        result = create_request(customer_id, request_type, description)
        return json.dumps(result, indent=2, default=str)
    except httpx.RequestError as e:
        return f"API Error: {e}"
    except Exception as e:
        return f"Error: {e}"


def demo_list_requests():
    """Handle request listing."""
    try:
        requests = list_requests()
        if not requests:
            return "No requests found."
        return json.dumps(requests, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"


def demo_get_request(request_id: str):
    """Handle getting a single request."""
    if not request_id:
        return "Error: Please provide a request ID"
    try:
        result = get_request(request_id)
        return json.dumps(result, indent=2, default=str)
    except httpx.HTTPStatusError:
        return "Not Found (404)"
    except Exception as e:
        return f"Error: {e}"


def demo_update_status(request_id: str, status: str, failure_reason: str = ""):
    """Handle status update."""
    if not request_id or not status:
        return "Error: Please provide request ID and status"
    try:
        result = update_request_status(request_id, status, failure_reason if status == "FAILED" else None)
        return json.dumps(result, indent=2, default=str)
    except httpx.HTTPStatusError as e:
        return f"HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error: {e}"


def demo_create_incident(title: str, description: str, severity: str):
    """Handle incident creation."""
    if not title or not description:
        return "Error: Please provide title and description"
    try:
        result = create_incident(title, description, severity)
        return json.dumps(result, indent=2, default=str)
    except httpx.RequestError as e:
        return f"API Error: {e}"
    except Exception as e:
        return f"Error: {e}"


def demo_get_health():
    """Handle health check."""
    try:
        result = get_health()
        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return f"Error: {e}"


def demo_get_metrics():
    """Handle metrics."""
    try:
        result = get_metrics()
        # Format as text for display
        lines = result["text"].split("\n")[:50]  # First 50 lines
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


def demo_get_requests_list():
    """Get requests for the table."""
    try:
        requests = list_requests()
        return [[r["request_id"], r["customer_id"], r["request_type"], r["status"], r["created_at"]] for r in requests]
    except Exception:
        return []


def demo_random_test():
    """Run a quick test workflow with random data."""
    customer_id = f"CUST-{random.randint(1000, 9999)}"
    test_cases = [
        ("SUPPORT", "Can't access my account"),
        ("BUG", "Page not loading correctly"),
        ("FEATURE", "Add dark mode option"),
    ]
    request_type, description = random.choice(test_cases)

    output = []
    output.append(f"Creating request for {customer_id}...")

    try:
        req = create_request(customer_id, request_type, description)
        output.append(f"Created: {req['request_id']}")

        # Update to processing
        status = update_request_status(req["request_id"], "PROCESSING")
        output.append(f"Updated to: {status['status']}")

        # Complete the request
        status = update_request_status(req["request_id"], "COMPLETED")
        output.append(f"Completed: {status['status']}")

        return "\n".join(output)
    except Exception as e:
        return f"Test failed: {e}"


# Gradio UI
with gr.Blocks(title="ServicePulse Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📡 ServicePulse Demo")
    gr.Markdown("A production-style operations platform demonstrating request lifecycle management and incident tracking.")

    with gr.Tab("Create Request"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create a New Request")
                customer_id = gr.Textbox(label="Customer ID", placeholder="CUST-123")
                request_type = gr.Dropdown(
                    choices=["SERVICE", "BUG", "FEATURE", "SUPPORT"],
                    label="Request Type",
                    value="SERVICE"
                )
                description = gr.Textbox(label="Description", lines=3, placeholder="Describe your request...")
                create_btn = gr.Button("Create Request", variant="primary")

            with gr.Column():
                create_output = gr.Code(label="Response", language="json")

        create_btn.click(
            demo_create_request,
            inputs=[customer_id, request_type, description],
            outputs=create_output
        )

    with gr.Tab("Request Management"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### List Requests")
                list_btn = gr.Button("Refresh List")

                gr.Markdown("### Get Request by ID")
                req_id_input = gr.Textbox(label="Request ID", placeholder="REQ-000001")
                get_req_btn = gr.Button("Get Request")

                gr.Markdown("### Update Status")
                update_req_id = gr.Textbox(label="Request ID")
                update_status = gr.Dropdown(
                    choices=["PROCESSING", "COMPLETED", "FAILED"],
                    label="New Status"
                )
                failure_reason = gr.Textbox(label="Failure Reason (optional)")
                update_btn = gr.Button("Update Status")

            with gr.Column():
                list_output = gr.Code(label="List Output", language="json")
                get_output = gr.Code(label="Get Output", language="json")
                update_output = gr.Code(label="Update Output", language="json")

        list_btn.click(demo_list_requests, outputs=list_output)
        get_req_btn.click(demo_get_request, inputs=req_id_input, outputs=get_output)
        update_btn.click(demo_update_status, inputs=[update_req_id, update_status, failure_reason], outputs=update_output)

    with gr.Tab("Incidents"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Create Incident")
                incident_title = gr.Textbox(label="Title", placeholder="Service outage...")
                incident_desc = gr.Textbox(label="Description", lines=3)
                severity = gr.Dropdown(
                    choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    label="Severity",
                    value="MEDIUM"
                )
                create_incident_btn = gr.Button("Create Incident", variant="primary")

            with gr.Column():
                incident_output = gr.Code(label="Response", language="json")

        create_incident_btn.click(demo_create_incident, inputs=[incident_title, incident_desc, severity], outputs=incident_output)

    with gr.Tab("Health & Metrics"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### System Health")
                health_btn = gr.Button("Check Health", variant="primary")
                health_output = gr.Code(label="Health Status", language="json")

            with gr.Column():
                gr.Markdown("### Prometheus Metrics")
                metrics_btn = gr.Button("Get Metrics")
                metrics_output = gr.Code(label="Metrics", language="text")

        health_btn.click(demo_get_health, outputs=health_output)
        metrics_btn.click(demo_get_metrics, outputs=metrics_output)

    with gr.Tab("Test Workflow"):
        gr.Markdown("### Run Test Workflow")
        gr.Markdown("This will create a random request, process it, and complete it to demonstrate the full lifecycle.")
        test_btn = gr.Button("Run Test", variant="secondary")
        test_output = gr.Textbox(label="Test Results")

        test_btn.click(demo_random_test, outputs=test_output)

    # Auto-refresh the list table periodically
    demo.load(demo_get_requests_list, outputs=gr.Dataframe())

    # Footer
    gr.Markdown("---")
    gr.Markdown("*ServicePulse v1.0.0 - Portfolio Demo*")


# Expose for Hugging Face Spaces
if __name__ == "__main__":
    demo.launch(share=True)
