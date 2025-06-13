# Multi-stage Dockerfile for PME Calculator Backend
# Stage 1: Builder - Install dependencies
FROM python:3.10-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pme_calculator/backend/pyproject.toml pme_calculator/backend/requirements.lock ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.lock

# Stage 2: Runtime - Create minimal production image
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy application code
COPY pme_calculator/backend/ ./backend/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main_minimal:app", "--host", "0.0.0.0", "--port", "8000"] 