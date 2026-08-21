# =============================================================================
# APPLICATION SERVICE - Dockerfile
# =============================================================================
# FastAPI + PostgreSQL Application Service
# Multi-stage build:
#   1. deps   -> installs Python dependencies
#   2. runner -> contains only what is required to run the application
# =============================================================================


# =============================================================================
# STAGE 1: "deps" - install Python dependencies
# =============================================================================
FROM python:3.12-slim AS deps

WORKDIR /app

# Update Debian packages and install build dependencies.
# apt-get upgrade ensures security fixes are applied to the base OS packages.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# =============================================================================
# STAGE 2: "runner" - final production image
# =============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Update Debian packages and install only the PostgreSQL runtime library.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*


# =============================================================================
# Copy installed Python packages from deps stage
# =============================================================================

COPY --from=deps /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

COPY --from=deps /usr/local/bin \
    /usr/local/bin


# =============================================================================
# Create non-root user
# =============================================================================

RUN groupadd -r appuser \
    && useradd -r -g appuser appuser


# =============================================================================
# Copy application files
# =============================================================================

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Startup script
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh


# =============================================================================
# Set permissions and switch to non-root user
# =============================================================================

RUN chown -R appuser:appuser /app

USER appuser


# =============================================================================
# Application configuration
# =============================================================================

# Application Service runs on port 8002
EXPOSE 8002


# =============================================================================
# Docker health check
# =============================================================================

HEALTHCHECK --interval=10s \
    --timeout=5s \
    --start-period=10s \
    --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')" || exit 1


# =============================================================================
# Start Application Service
# =============================================================================

CMD ["./entrypoint.sh"]
