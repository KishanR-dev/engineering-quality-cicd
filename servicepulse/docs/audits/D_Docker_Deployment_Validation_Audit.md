commit 3ca0c600cc1e86f5d9caf8c0d1499dd4610098f2
Author: KishanR-dev <kishram2002@gmail.com>
Date:   Sat Oct 3 16:28:33 2026 +0530

    Enhance Gradio app with in-process FastAPI TestClient execution
    
    Co-Authored-By: Claude Code <noreply@anthropic.com>

diff --git a/servicepulse/app.py b/servicepulse/app.py
index e3891e3..240e10a 100644
--- a/servicepulse/app.py
+++ b/servicepulse/app.py
@@ -1,350 +1,357 @@
-"""Gradio interface for Hugging Face Spaces deployment.
+"""ServicePulse - Gradio Interface for Interactive Demonstration.
 
-This module provides a demo interface that exercises ServicePulse functionality
-through its REST API. The interface uses the internal FastAPI app for all logic.
+Production-style operations platform demonstrating request lifecycle management
+and incident tracking. Powered by FastAPI and SQLite backend.
 """
 
+from __future__ import annotations
+
 import json
 import random
-import sqlite3
-from pathlib import Path
+from typing import Any
 
 import gradio as gr
-import httpx
-
-# Configuration for Spaces
-BASE_URL = "http://127.0.0.1:7860"
-DATA_DIR = Path("/app/data")
-DB_PATH = DATA_DIR / "servicepulse.db"
-
-
-def get_db_connection():
-    """Get database connection for the demo."""
-    conn = sqlite3.connect(DB_PATH)
-    conn.row_factory = sqlite3.Row
-    return conn
-
-
-def get_requests_list():
-    """Get list of requests for the demo table."""
-    if not DB_PATH.exists():
-        return []
-    conn = get_db_connection()
-    try:
-        cursor = conn.execute(
-            "SELECT request_id, customer_id, request_type, status, created_at FROM service_requests ORDER BY created_at DESC LIMIT 20"
-        )
-        rows = cursor.fetchall()
-        return [dict(row) for row in rows]
-    finally:
-        conn.close()
+from fastapi.testclient import TestClient
 
+# ZeroGPU support check (if deployed on Hugging Face Spaces with ZeroGPU)
+try:
+    import spaces
 
-def create_request(customer_id: str, request_type: str, description: str) -> dict:
-    """Create a request using the FastAPI app."""
-    with httpx.Client(timeout=10.0) as client:
-        response = client.post(
-            f"{BASE_URL}/api/v1/requests",
-            json={
-                "customer_id": customer_id,
-                "request_type": request_type,
-                "description": description,
-            },
-        )
-        response.raise_for_status()
-        return response.json()
+    @spaces.GPU
+    def _zero_gpu_startup():
+        """Satisfy Hugging Face ZeroGPU startup check."""
+        return True
 
+    _zero_gpu_startup()
+except Exception:
+    pass
 
-def list_requests() -> list:
-    """List requests."""
-    with httpx.Client(timeout=10.0) as client:
-        response = client.get(f"{BASE_URL}/api/v1/requests")
-        response.raise_for_status()
-        data = response.json()
-        return data.get("items", [])
+# Initialize ServicePulse FastAPI application and database
+from app.db.database import init_db  # noqa: E402
+from app.main import app as fastapi_app  # noqa: E402
 
+init_db()
+client = TestClient(fastapi_app)
 
-def get_request(request_id: str) -> dict:
-    """Get a single request."""
-    with httpx.Client(timeout=10.0) as client:
-        response = client.get(f"{BASE_URL}/api/v1/requests/{request_id}")
-        response.raise_for_status()
-        return response.json()
 
+def _format_json(data: Any) -> str:
+    """Helper to pretty-print JSON responses."""
+    return json.dumps(data, indent=2, default=str)
 
-def update_request_status(request_id: str, status: str, failure_reason: str = None) -> dict:
-    """Update request status."""
-    payload = {"status": status}
-    if failure_reason:
-        payload["failure_reason"] = failure_reason
-    with httpx.Client(timeout=10.0) as client:
-        response = client.patch(
-            f"{BASE_URL}/api/v1/requests/{request_id}/status",
-            json=payload,
-        )
-        response.raise_for_status()
-        return response.json()
 
+def create_request_handler(customer_id: str, request_type: str, description: str) -> str:
+    """Handle service request creation."""
+    if not customer_id or not customer_id.strip():
+        return "Error: Customer ID is required (format: CUST-XXX, e.g., CUST-001)"
+    if not description or not description.strip():
+        return "Error: Description is required"
 
-def create_incident(title: str, description: str, severity: str) -> dict:
-    """Create an incident."""
-    with httpx.Client(timeout=10.0) as client:
+    try:
         response = client.post(
-            f"{BASE_URL}/api/v1/incidents",
+            "/api/v1/requests",
             json={
-                "title": title,
-                "description": description,
-                "severity": severity,
-                "affected_service": "servicepulse_demo",
+                "customer_id": customer_id.strip(),
+                "request_type": request_type,
+                "description": description.strip(),
             },
         )
-        response.raise_for_status()
-        return response.json()
-
-
-def get_health() -> dict:
-    """Get health status."""
-    with httpx.Client(timeout=10.0) as client:
-        response = client.get(f"{BASE_URL}/health")
-        response.raise_for_status()
-        return response.json()
-
-
-def get_metrics() -> dict:
-    """Get metrics."""
-    with httpx.Client(timeout=10.0) as client:
-        response = client.get(f"{BASE_URL}/api/v1/metrics")
-        response.raise_for_status()
-        return {"text": response.text}
+        if response.status_code == 201:
+            return _format_json(response.json())
+        return f"Status {response.status_code}:\n{_format_json(response.json())}"
+    except Exception as e:
+        return f"Internal Error: {e}"
 
 
-# Demo functions for Gradio interface
-def demo_create_request(customer_id: str, request_type: str, description: str):
-    """Handle request creation."""
-    if not customer_id or not description:
-        return "Error: Please provide customer ID and description"
+def list_requests_handler() -> str:
+    """Handle listing service requests."""
     try:
-        result = create_request(customer_id, request_type, description)
-        return json.dumps(result, indent=2, default=str)
-    except httpx.RequestError as e:
-        return f"API Error: {e}"
+        response = client.get("/api/v1/requests")
+        if response.status_code == 200:
+            return _format_json(response.json())
+        return f"Status {response.status_code}:\n{_format_json(response.json())}"
     except Exception as e:
-        return f"Error: {e}"
+        return f"Internal Error: {e}"
+
 
+def get_request_handler(request_id: str) -> str:
+    """Handle fetching a single service request by ID."""
+    if not request_id or not request_id.strip():
+        return "Error: Request ID is required (e.g., REQ-000001)"
 
-def demo_list_requests():
-    """Handle request listing."""
     try:
-        requests = list_requests()
-        if not requests:
-            return "No requests found."
-        return json.dumps(requests, indent=2, default=str)
+        response = client.get(f"/api/v1/requests/{request_id.strip()}")
+        if response.status_code == 200:
+            return _format_json(response.json())
+        elif response.status_code == 404:
+            return f"Not Found (404): Request '{request_id.strip()}' does not exist."
+        return f"Status {response.status_code}:\n{_format_json(response.json())}"
     except Exception as e:
-        return f"Error: {e}"
+        return f"Internal Error: {e}"
 
 
-def demo_get_request(request_id: str):
-    """Handle getting a single request."""
-    if not request_id:
-        return "Error: Please provide a request ID"
-    try:
-        result = get_request(request_id)
-        return json.dumps(result, indent=2, default=str)
-    except httpx.HTTPStatusError:
-        return "Not Found (404)"
-    except Exception as e:
-        return f"Error: {e}"
+def update_status_handler(request_id: str, status: str, failure_reason: str = "") -> str:
+    """Handle request lifecycle status updates."""
+    if not request_id or not request_id.strip():
+        return "Error: Request ID is required"
+    if not status:
+        return "Error: Target status is required"
 
+    payload: dict[str, Any] = {"status": status}
+    if status == "FAILED" and failure_reason and failure_reason.strip():
+        payload["failure_reason"] = failure_reason.strip()
 
-def demo_update_status(request_id: str, status: str, failure_reason: str = ""):
-    """Handle status update."""
-    if not request_id or not status:
-        return "Error: Please provide request ID and status"
     try:
-        result = update_request_status(request_id, status, failure_reason if status == "FAILED" else None)
-        return json.dumps(result, indent=2, default=str)
-    except httpx.HTTPStatusError as e:
-        return f"HTTP {e.response.status_code}: {e.response.text}"
+        response = client.patch(
+            f"/api/v1/requests/{request_id.strip()}/status",
+            json=payload,
+        )
+        if response.status_code == 200:
+            return _format_json(response.json())
+        return f"Status {response.status_code}:\n{_format_json(response.json())}"
     except Exception as e:
-        return f"Error: {e}"
+        return f"Internal Error: {e}"
 
 
-def demo_create_incident(title: str, description: str, severity: str):
+def create_incident_handler(title: str, description: str, severity: str) -> str:
     """Handle incident creation."""
-    if not title or not description:
-        return "Error: Please provide title and description"
+    if not title or not title.strip():
+        return "Error: Incident Title is required"
+    if not description or not description.strip():
+        return "Error: Incident Description is required"
+
     try:
-        result = create_incident(title, description, severity)
-        return json.dumps(result, indent=2, default=str)
-    except httpx.RequestError as e:
-        return f"API Error: {e}"
+        response = client.post(
+            "/api/v1/incidents",
+            json={
+                "title": title.strip(),
+                "description": description.strip(),
+                "severity": severity,
+                "affected_service": "servicepulse_core",
+            },
+        )
+        if response.status_code == 201:
+            return _format_json(response.json())
+        return f"Status {response.status_code}:\n{_format_json(response.json())}"
     except Exception as e:
-        return f"Error: {e}"
+        return f"Internal Error: {e}"
 
 
-def demo_get_health():
-    """Handle health check."""
+def get_health_handler() -> str:
+    """Handle health check endpoint."""
     try:
-        result = get_health()
-        return json.dumps(result, indent=2, default=str)
+        response = client.get("/health")
+        return _format_json(response.json())
     except Exception as e:
-        return f"Error: {e}"
+        return f"Internal Error: {e}"
 
 
-def demo_get_metrics():
-    """Handle metrics."""
+def get_metrics_handler() -> str:
+    """Handle Prometheus metrics endpoint."""
     try:
-        result = get_metrics()
-        # Format as text for display
-        lines = result["text"].split("\n")[:50]  # First 50 lines
+        response = client.get("/api/v1/metrics")
+        lines = response.text.split("\n")[:40]
         return "\n".join(lines)
     except Exception as e:
-        return f"Error: {e}"
+        return f"Internal Error: {e}"
 
 
-def demo_get_requests_list():
-    """Get requests for the table."""
+def get_requests_table_data() -> list[list[str]]:
+    """Fetch request rows for table view."""
     try:
-        requests = list_requests()
-        return [[r["request_id"], r["customer_id"], r["request_type"], r["status"], r["created_at"]] for r in requests]
+        response = client.get("/api/v1/requests?limit=25")
+        if response.status_code == 200:
+            items = response.json().get("items", [])
+            return [
+                [
+                    item.get("request_id", ""),
+                    item.get("customer_id", ""),
+                    item.get("request_type", ""),
+                    item.get("status", ""),
+                    str(item.get("created_at", "")),
+                ]
+                for item in items
+            ]
+        return []
     except Exception:
         return []
 
 
-def demo_random_test():
-    """Run a quick test workflow with random data."""
-    customer_id = f"CUST-{random.randint(1000, 9999)}"
+def run_automated_workflow() -> str:
+    """Execute end-to-end automated demonstration workflow."""
+    customer_num = random.randint(100, 999)
+    customer_id = f"CUST-{customer_num}"
     test_cases = [
-        ("SUPPORT", "Can't access my account"),
-        ("BUG", "Page not loading correctly"),
-        ("FEATURE", "Add dark mode option"),
+        ("SERVICE", "Automated customer account validation"),
+        ("BUG", "Payment retry mechanism validation"),
+        ("FEATURE", "Automated export service dispatch"),
+        ("SUPPORT", "High-priority onboarding verification"),
     ]
-    request_type, description = random.choice(test_cases)
-
-    output = []
-    output.append(f"Creating request for {customer_id}...")
-
-    try:
-        req = create_request(customer_id, request_type, description)
-        output.append(f"Created: {req['request_id']}")
-
-        # Update to processing
-        status = update_request_status(req["request_id"], "PROCESSING")
-        output.append(f"Updated to: {status['status']}")
-
-        # Complete the request
-        status = update_request_status(req["request_id"], "COMPLETED")
-        output.append(f"Completed: {status['status']}")
-
-        return "\n".join(output)
-    except Exception as e:
-        return f"Test failed: {e}"
-
-
-# Gradio UI
-with gr.Blocks(title="ServicePulse Demo", theme=gr.themes.Soft()) as demo:
-    gr.Markdown("# 📡 ServicePulse Demo")
-    gr.Markdown("A production-style operations platform demonstrating request lifecycle management and incident tracking.")
+    req_type, desc = random.choice(test_cases)
+
+    steps = [f"=== Starting Automated Demo Workflow for {customer_id} ==="]
+
+    # Step 1: Create Request
+    create_resp = client.post(
+        "/api/v1/requests",
+        json={"customer_id": customer_id, "request_type": req_type, "description": desc},
+    )
+    if create_resp.status_code != 201:
+        steps.append(f"Step 1 Failed: {create_resp.text}")
+        return "\n".join(steps)
+
+    req_data = create_resp.json()
+    req_id = req_data["request_id"]
+    steps.append(f"1. Created Request: {req_id} [Status: {req_data['status']}, Type: {req_type}]")
+
+    # Step 2: Transition to PROCESSING
+    proc_resp = client.patch(
+        f"/api/v1/requests/{req_id}/status",
+        json={"status": "PROCESSING"},
+    )
+    if proc_resp.status_code != 200:
+        steps.append(f"Step 2 Failed: {proc_resp.text}")
+        return "\n".join(steps)
+
+    steps.append(f"2. Processing: {req_id} transitioned to PROCESSING")
+
+    # Step 3: Transition to COMPLETED
+    comp_resp = client.patch(
+        f"/api/v1/requests/{req_id}/status",
+        json={"status": "COMPLETED"},
+    )
+    if comp_resp.status_code != 200:
+        steps.append(f"Step 3 Failed: {comp_resp.text}")
+        return "\n".join(steps)
+
+    steps.append(f"3. Lifecycle Complete: {req_id} transitioned to COMPLETED successfully!")
+    steps.append("=== Workflow Completed Successfully ===")
+    return "\n".join(steps)
+
+
+# Build Gradio UI
+with gr.Blocks(title="ServicePulse Demo") as demo:
+    gr.Markdown("# ServicePulse Demo")
+    gr.Markdown(
+        "A production-style operations platform demonstrating request lifecycle management, "
+        "incident tracking, and operational observability."
+    )
 
     with gr.Tab("Create Request"):
         with gr.Row():
             with gr.Column():
-                gr.Markdown("### Create a New Request")
-                customer_id = gr.Textbox(label="Customer ID", placeholder="CUST-123")
-                request_type = gr.Dropdown(
+                gr.Markdown("### Submit New Request")
+                cust_input = gr.Textbox(
+                    label="Customer ID",
+                    value="CUST-001",
+                    placeholder="e.g. CUST-001 or CUST-100",
+                )
+                type_input = gr.Dropdown(
                     choices=["SERVICE", "BUG", "FEATURE", "SUPPORT"],
+                    value="SERVICE",
                     label="Request Type",
-                    value="SERVICE"
                 )
-                description = gr.Textbox(label="Description", lines=3, placeholder="Describe your request...")
+                desc_input = gr.Textbox(
+                    label="Description",
+                    value="User onboarding checklist verification",
+                    lines=3,
+                )
                 create_btn = gr.Button("Create Request", variant="primary")
-
             with gr.Column():
-                create_output = gr.Code(label="Response", language="json")
+                create_out = gr.Code(label="API Response", language="json")
 
         create_btn.click(
-            demo_create_request,
-            inputs=[customer_id, request_type, description],
-            outputs=create_output
+            create_request_handler,
+            inputs=[cust_input, type_input, desc_input],
+            outputs=create_out,
         )
 
     with gr.Tab("Request Management"):
         with gr.Row():
             with gr.Column():
-                gr.Markdown("### List Requests")
-                list_btn = gr.Button("Refresh List")
+                gr.Markdown("### Look Up Request")
+                lookup_id = gr.Textbox(label="Request ID", placeholder="e.g. REQ-000001")
+                lookup_btn = gr.Button("Get Request Details")
 
-                gr.Markdown("### Get Request by ID")
-                req_id_input = gr.Textbox(label="Request ID", placeholder="REQ-000001")
-                get_req_btn = gr.Button("Get Request")
-
-                gr.Markdown("### Update Status")
-                update_req_id = gr.Textbox(label="Request ID")
-                update_status = gr.Dropdown(
+                gr.Markdown("### Update Lifecycle Status")
+                status_id = gr.Textbox(label="Request ID for Status Update")
+                new_status = gr.Dropdown(
                     choices=["PROCESSING", "COMPLETED", "FAILED"],
-                    label="New Status"
+                    value="PROCESSING",
+                    label="Target Status",
                 )
-                failure_reason = gr.Textbox(label="Failure Reason (optional)")
-                update_btn = gr.Button("Update Status")
-
+                fail_reason = gr.Textbox(label="Failure Reason (Required for FAILED)")
+                update_btn = gr.Button("Update Status", variant="primary")
             with gr.Column():
-                list_output = gr.Code(label="List Output", language="json")
-                get_output = gr.Code(label="Get Output", language="json")
-                update_output = gr.Code(label="Update Output", language="json")
-
-        list_btn.click(demo_list_requests, outputs=list_output)
-        get_req_btn.click(demo_get_request, inputs=req_id_input, outputs=get_output)
-        update_btn.click(demo_update_status, inputs=[update_req_id, update_status, failure_reason], outputs=update_output)
+                lookup_out = gr.Code(label="Lookup Output", language="json")
+                update_out = gr.Code(label="Update Output", language="json")
+
+        lookup_btn.click(get_request_handler, inputs=lookup_id, outputs=lookup_out)
+        update_btn.click(
+            update_status_handler,
+            inputs=[status_id, new_status, fail_reason],
+            outputs=update_out,
+        )
 
     with gr.Tab("Incidents"):
         with gr.Row():
             with gr.Column():
-                gr.Markdown("### Create Incident")
-                incident_title = gr.Textbox(label="Title", placeholder="Service outage...")
-                incident_desc = gr.Textbox(label="Description", lines=3)
-                severity = gr.Dropdown(
+                gr.Markdown("### Log New Incident")
+                inc_title = gr.Textbox(label="Title", placeholder="e.g. Gateway Latency Spike")
+                inc_desc = gr.Textbox(
+                    label="Description",
+                    placeholder="Describe impact, affected components, and symptoms...",
+                    lines=3,
+                )
+                inc_sev = gr.Dropdown(
                     choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
+                    value="MEDIUM",
                     label="Severity",
-                    value="MEDIUM"
                 )
-                create_incident_btn = gr.Button("Create Incident", variant="primary")
-
+                inc_btn = gr.Button("Create Incident", variant="primary")
             with gr.Column():
-                incident_output = gr.Code(label="Response", language="json")
+                inc_out = gr.Code(label="Incident Response", language="json")
 
-        create_incident_btn.click(demo_create_incident, inputs=[incident_title, incident_desc, severity], outputs=incident_output)
+        inc_btn.click(
+            create_incident_handler,
+            inputs=[inc_title, inc_desc, inc_sev],
+            outputs=inc_out,
+        )
 
-    with gr.Tab("Health & Metrics"):
+    with gr.Tab("Health & Observability"):
         with gr.Row():
             with gr.Column():
-                gr.Markdown("### System Health")
-                health_btn = gr.Button("Check Health", variant="primary")
-                health_output = gr.Code(label="Health Status", language="json")
-
+                gr.Markdown("### Health Check (`/health`)")
+                health_btn = gr.Button("Check System Health", variant="primary")
+                health_out = gr.Code(label="Health Status", language="json")
             with gr.Column():
-                gr.Markdown("### Prometheus Metrics")
-                metrics_btn = gr.Button("Get Metrics")
-                metrics_output = gr.Code(label="Metrics", language="text")
-
-        health_btn.click(demo_get_health, outputs=health_output)
-        metrics_btn.click(demo_get_metrics, outputs=metrics_output)
-
-    with gr.Tab("Test Workflow"):
-        gr.Markdown("### Run Test Workflow")
-        gr.Markdown("This will create a random request, process it, and complete it to demonstrate the full lifecycle.")
-        test_btn = gr.Button("Run Test", variant="secondary")
-        test_output = gr.Textbox(label="Test Results")
-
-        test_btn.click(demo_random_test, outputs=test_output)
-
-    # Auto-refresh the list table periodically
-    demo.load(demo_get_requests_list, outputs=gr.Dataframe())
+                gr.Markdown("### Prometheus Metrics (`/api/v1/metrics`)")
+                metrics_btn = gr.Button("Fetch Metrics")
+                metrics_out = gr.Textbox(label="Metrics Stream", lines=20)
+
+        health_btn.click(get_health_handler, outputs=health_out)
+        metrics_btn.click(get_metrics_handler, outputs=metrics_out)
+
+    with gr.Tab("Automated Test Workflow"):
+        gr.Markdown("### Run Automated Lifecycle Demonstration")
+        gr.Markdown("Simulates a complete request creation, state transitions, and completion.")
+        test_btn = gr.Button("Run Lifecycle Test", variant="secondary")
+        test_out = gr.Textbox(label="Workflow Execution Log", lines=8)
+        test_btn.click(run_automated_workflow, outputs=test_out)
+
+    with gr.Tab("Live Requests Feed"):
+        gr.Markdown("### Current Requests in Database")
+        refresh_feed_btn = gr.Button("Refresh Table")
+        table_out = gr.Dataframe(
+            headers=["Request ID", "Customer ID", "Type", "Status", "Created At"],
+            datatype=["str", "str", "str", "str", "str"],
+        )
+        refresh_feed_btn.click(get_requests_table_data, outputs=table_out)
+        demo.load(get_requests_table_data, outputs=table_out)
 
-    # Footer
     gr.Markdown("---")
-    gr.Markdown("*ServicePulse v1.0.0 - Portfolio Demo*")
-
+    gr.Markdown(
+        "*ServicePulse v1.0.0 — Production Operations & Incident Management Platform*"
+    )
 
-# Expose for Hugging Face Spaces
 if __name__ == "__main__":
-    demo.launch(share=True)
+    demo.launch()

commit ef9979cd62cd573ecf86df21d59b29227e995a44
Author: KishanR-dev <kishram2002@gmail.com>
Date:   Sat Oct 3 11:20:07 2026 +0530

    Update for Hugging Face Spaces Gradio deployment
    
    - Switched from Docker-based to Gradio interface (free-tier compatible)
    - Updated requirements.txt with gradio==6.26.0
    - Created interactive web interface with request/incident management
    - Added test workflow demonstration
    
    The Gradio interface provides:
    - Request CRUD operations
    - Incident creation
    - Health check and metrics endpoints
    - One-click test workflow

diff --git a/servicepulse/app.py b/servicepulse/app.py
index 9f65260..e3891e3 100644
--- a/servicepulse/app.py
+++ b/servicepulse/app.py
@@ -1,27 +1,350 @@
-"""Hugging Face Spaces entry point.
+"""Gradio interface for Hugging Face Spaces deployment.
 
-This module is used by Hugging Face Spaces to run the FastAPI application.
-The Spaces Docker configuration will use this file as the entry point.
+This module provides a demo interface that exercises ServicePulse functionality
+through its REST API. The interface uses the internal FastAPI app for all logic.
 """
 
-import os
+import json
+import random
+import sqlite3
+from pathlib import Path
 
-# Hugging Face Spaces runs on port 7860 by default
-os.environ.setdefault("APP_HOST", "0.0.0.0")
-os.environ.setdefault("APP_PORT", "7860")
-os.environ.setdefault("APP_ENV", "production")
-os.environ.setdefault("DATABASE_URL", "sqlite:////app/data/servicepulse.db")
+import gradio as gr
+import httpx
 
-# Ensure failure simulation is disabled in production
-os.environ.setdefault("FAILURE_SIMULATION_ENABLED", "false")
+# Configuration for Spaces
+BASE_URL = "http://127.0.0.1:7860"
+DATA_DIR = Path("/app/data")
+DB_PATH = DATA_DIR / "servicepulse.db"
 
-from app.main import app  # noqa: E402
 
-# Expose for Spaces
-app.title = "ServicePulse"
-app.version = "1.0.0"
+def get_db_connection():
+    """Get database connection for the demo."""
+    conn = sqlite3.connect(DB_PATH)
+    conn.row_factory = sqlite3.Row
+    return conn
 
+
+def get_requests_list():
+    """Get list of requests for the demo table."""
+    if not DB_PATH.exists():
+        return []
+    conn = get_db_connection()
+    try:
+        cursor = conn.execute(
+            "SELECT request_id, customer_id, request_type, status, created_at FROM service_requests ORDER BY created_at DESC LIMIT 20"
+        )
+        rows = cursor.fetchall()
+        return [dict(row) for row in rows]
+    finally:
+        conn.close()
+
+
+def create_request(customer_id: str, request_type: str, description: str) -> dict:
+    """Create a request using the FastAPI app."""
+    with httpx.Client(timeout=10.0) as client:
+        response = client.post(
+            f"{BASE_URL}/api/v1/requests",
+            json={
+                "customer_id": customer_id,
+                "request_type": request_type,
+                "description": description,
+            },
+        )
+        response.raise_for_status()
+        return response.json()
+
+
+def list_requests() -> list:
+    """List requests."""
+    with httpx.Client(timeout=10.0) as client:
+        response = client.get(f"{BASE_URL}/api/v1/requests")
+        response.raise_for_status()
+        data = response.json()
+        return data.get("items", [])
+
+
+def get_request(request_id: str) -> dict:
+    """Get a single request."""
+    with httpx.Client(timeout=10.0) as client:
+        response = client.get(f"{BASE_URL}/api/v1/requests/{request_id}")
+        response.raise_for_status()
+        return response.json()
+
+
+def update_request_status(request_id: str, status: str, failure_reason: str = None) -> dict:
+    """Update request status."""
+    payload = {"status": status}
+    if failure_reason:
+        payload["failure_reason"] = failure_reason
+    with httpx.Client(timeout=10.0) as client:
+        response = client.patch(
+            f"{BASE_URL}/api/v1/requests/{request_id}/status",
+            json=payload,
+        )
+        response.raise_for_status()
+        return response.json()
+
+
+def create_incident(title: str, description: str, severity: str) -> dict:
+    """Create an incident."""
+    with httpx.Client(timeout=10.0) as client:
+        response = client.post(
+            f"{BASE_URL}/api/v1/incidents",
+            json={
+                "title": title,
+                "description": description,
+                "severity": severity,
+                "affected_service": "servicepulse_demo",
+            },
+        )
+        response.raise_for_status()
+        return response.json()
+
+
+def get_health() -> dict:
+    """Get health status."""
+    with httpx.Client(timeout=10.0) as client:
+        response = client.get(f"{BASE_URL}/health")
+        response.raise_for_status()
+        return response.json()
+
+
+def get_metrics() -> dict:
+    """Get metrics."""
+    with httpx.Client(timeout=10.0) as client:
+        response = client.get(f"{BASE_URL}/api/v1/metrics")
+        response.raise_for_status()
+        return {"text": response.text}
+
+
+# Demo functions for Gradio interface
+def demo_create_request(customer_id: str, request_type: str, description: str):
+