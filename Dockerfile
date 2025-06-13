# Multi-stage Dockerfile for PME Calculator
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy requirements files
COPY requirements/base.txt .
COPY requirements.txt .

# Install dependencies using --prefix to /install
RUN pip install --prefix=/install --no-cache-dir -r base.txt
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Copy application code for building
COPY pme_app/ ./pme_app/
COPY setup.py .

# Install the package itself (not in editable mode for Docker)
RUN pip install --prefix=/install --no-deps .

# Stage 2: Runtime - Create minimal production image
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder stage to /usr/local
COPY --from=builder /install /usr/local

# Copy application code
COPY pme_app/ ./pme_app/
COPY setup.py .

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