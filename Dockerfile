# Multi-stage Dockerfile for PME Calculator
FROM python:3.13-slim AS builder

WORKDIR /app

# Copy setup files
COPY setup.py .
COPY pyproject.toml .
COPY pme_app/ ./pme_app/
COPY pme_calculator/ ./pme_calculator/
COPY pme_math/ ./pme_math/

# Install dependencies and the package itself
RUN pip install --prefix=/install --no-cache-dir -e .[dev]

# Stage 2: Runtime - Create minimal production image
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder stage to /usr/local
COPY --from=builder /install /usr/local

# Copy application code
COPY pme_app/ ./pme_app/
COPY pme_calculator/ ./pme_calculator/
COPY pme_math/ ./pme_math/
COPY setup.py .
COPY pyproject.toml .

# Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Verify CLI works
RUN python -m pme_app.cli --help

# Run the application
CMD ["uvicorn", "pme_app.main:app", "--host", "0.0.0.0", "--port", "8000"] 