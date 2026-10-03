# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim AS production

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application
COPY app ./app
COPY pyproject.toml .

# Create writable data directory for SQLite
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

ENV PYTHONPATH=/app
ENV APP_ENV=production
ENV DATABASE_URL=sqlite:////app/data/servicepulse.db

# Port is configurable via environment variable (default 7860 for Hugging Face Spaces)
EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
