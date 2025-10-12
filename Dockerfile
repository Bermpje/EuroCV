# Multi-stage Dockerfile for EuroCV
# Optimized for size and security

# Stage 1: Builder
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code and project files
COPY src/ /app/src/
COPY pyproject.toml /app/
COPY setup.py /app/
COPY README.md /app/

WORKDIR /app

# Upgrade pip and setuptools to ensure pyproject.toml support
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install the package with all dependencies from pyproject.toml
# Using verbose mode to see what's being installed
RUN pip install --no-cache-dir -v ".[ocr]"


# Stage 2: Runtime
FROM python:3.11-slim

# Install runtime dependencies including Tesseract for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-nld \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN useradd -m -u 1000 eurocv && \
    mkdir -p /data && \
    chown -R eurocv:eurocv /data

# Set working directory
WORKDIR /data

# Switch to non-root user
USER eurocv

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import eurocv; print('OK')" || exit 1

# Default command
ENTRYPOINT ["eurocv"]
CMD ["--help"]

# Labels
LABEL maintainer="Emiel Kremers" \
      description="Convert resumes to Europass format" \
      version="0.1.0"
