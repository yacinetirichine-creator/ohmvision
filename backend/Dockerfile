# OhmVision Backend - Dockerfile
# ================================
# Compatible Railway, Render, et autres PaaS
# Multi-stage build with optional GPU support

ARG USE_GPU=false
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
COPY requirements-gpu.txt* ./

# Install Python dependencies (CPU by default)
RUN if [ "$USE_GPU" = "true" ] && [ -f requirements-gpu.txt ]; then \
        pip install --no-cache-dir -r requirements-gpu.txt ; \
    else \
        pip install --no-cache-dir -r requirements.txt ; \
    fi

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /app/uploads /app/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Expose port (Railway uses $PORT)
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application - Railway injects $PORT automatically
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
