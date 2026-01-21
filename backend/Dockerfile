# OhmVision Backend - Dockerfile
# ================================
# Compatible Railway Pro, Render, et autres PaaS
# Version complète avec IA (PyTorch, YOLO, OpenCV)

ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /app

# Install system dependencies (full version with OpenCV support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies (FULL version with AI)
RUN pip install --no-cache-dir -r requirements.txt

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
