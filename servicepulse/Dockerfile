# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir pip-tools

COPY servicepulse/requirements.txt .
RUN pip-compile --no-emit-index-url requirements.txt

# Copy application source
COPY servicepulse/ .

# Install production dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy installed packages from builder
COPY --from=builder /build/requirements.txt .

# Copy application
COPY --from=builder /build/app ./app
COPY --from=builder /build/pyproject.toml .

# Create data directory for database
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
