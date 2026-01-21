# OhmVision Backend - Dockerfile
# ================================
# Compatible Railway, Render, et autres PaaS
# Version optimisée pour Railway (limite 4GB)

ARG PYTHON_VERSION=3.11
ARG LIGHT_MODE=true

FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first (for better caching)
COPY requirements-light.txt .
COPY requirements.txt .

# Install Python dependencies (LIGHT version for Railway free tier)
RUN pip install --no-cache-dir -r requirements-light.txt

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
