"""Route modules.

Each route module should have a `register(app)` function that adds routes to the FastAPI app.
This allows for circular import-free routing.
"""

def register_all(app):
    """Register all route modules to the app."""
    from app.api.routes import health, requests, incidents, metrics
    app.include_router(health.router)
    app.include_router(requests.router, prefix="/api/v1")
    app.include_router(incidents.router, prefix="/api/v1")
    app.include_router(metrics.router, prefix="/api/v1")
