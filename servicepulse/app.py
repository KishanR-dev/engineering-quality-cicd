"""Hugging Face Spaces entry point.

This module is used by Hugging Face Spaces to run the FastAPI application.
The Spaces Docker configuration will use this file as the entry point.
"""

import os

# Hugging Face Spaces runs on port 7860 by default
os.environ.setdefault("APP_HOST", "0.0.0.0")
os.environ.setdefault("APP_PORT", "7860")
os.environ.setdefault("APP_ENV", "production")
os.environ.setdefault("DATABASE_URL", "sqlite:////app/data/servicepulse.db")

# Ensure failure simulation is disabled in production
os.environ.setdefault("FAILURE_SIMULATION_ENABLED", "false")

from app.main import app  # noqa: E402

# Expose for Spaces
app.title = "ServicePulse"
app.version = "1.0.0"

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
