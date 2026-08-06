# =============================================================================
# CREDIT DECISION SERVICE - Dockerfile
# =============================================================================
# This builds a container image for the Credit Decision Service (FastAPI +
# PostgreSQL). Same multi-stage pattern as Auth Service - see that file's
# comments for the full explanation of WHY each step exists. This service
# is the simplest of the three - it has no JWT/authentication dependencies,
# since it's only ever called internally by Application Service, never
# directly by end users.
# =============================================================================


# =============================================================================
# STAGE 1: "deps" - temporary stage, only used to install Python packages
# =============================================================================
FROM python:3.12-slim AS deps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# =============================================================================
# STAGE 2: "runner" - this becomes the ACTUAL final image
# =============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN chown -R appuser:appuser /app
USER appuser

# Credit Decision Service listens on 8003 (Auth uses 8001, Application uses 8002).
EXPOSE 8003

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/health')" || exit 1

# The ONE main command: runs entrypoint.sh (migrate, then start uvicorn).
CMD ["./entrypoint.sh"]
