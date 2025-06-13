# Multi-stage Dockerfile for PME Calculator
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy requirements files
COPY requirements/base.txt .

# Install dependencies
RUN pip install --user --no-cache-dir -r base.txt

# Stage 2: Runtime - Create minimal production image
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Add local packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY pme_app/ ./pme_app/
COPY setup.py .

# Install the package
RUN pip install --user -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "pme_app.main:app", "--host", "0.0.0.0", "--port", "8000"] 