# =============================================================================
# AUTH SERVICE - Dockerfile
# =============================================================================
# This builds a container image for the Auth Service (FastAPI + PostgreSQL).
# We use a "multi-stage build" - meaning this file has TWO separate FROM
# sections. Only the LAST stage becomes the final image; earlier stages are
# just temporary workspaces used to prepare things, then thrown away.
#
# Why multi-stage? Some Python packages (like asyncpg, bcrypt) need a C
# compiler (gcc) to install. We only need that compiler ONCE, during
# installation - not in the final running container. Splitting into stages
# means our final image doesn't carry that extra weight around.
# =============================================================================


# =============================================================================
# STAGE 1: "deps" - a temporary stage, only used to install Python packages
# =============================================================================
FROM python:3.12-slim-bookworm AS deps
# python:3.12-slim = a smaller version of the official Python image.
# We use "slim" (not "alpine") because Alpine uses a different C library
# (musl instead of glibc) that frequently breaks packages like asyncpg
# and bcrypt in confusing ways. Slim is a safer, more reliable choice.

WORKDIR /app
# All following commands run inside /app inside the container.

# Install build tools needed ONLY to compile some Python packages.
# gcc = C compiler, libpq-dev = PostgreSQL client library headers.
# These are deleted from the final image later (they only exist in this stage).
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# "rm -rf /var/lib/apt/lists/*" clears apt's package cache to keep the
# image smaller - standard practice in every apt-get RUN command.

# Copy ONLY requirements.txt first (not the whole app yet).
# This is a deliberate Docker performance trick: Docker caches each step.
# If requirements.txt hasn't changed, Docker reuses the cached "pip install"
# result instead of re-running it - much faster rebuilds during development.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# =============================================================================
# STAGE 2: "runner" - this becomes the ACTUAL final image
# =============================================================================
FROM python:3.12-slim-bookworm AS runner
# Starting fresh from python:3.12-slim again - NONE of the gcc/libpq-dev
# build tools from Stage 1 carry over. Only what we explicitly COPY below.

WORKDIR /app

# Install only the lightweight RUNTIME library needed to talk to PostgreSQL.
# libpq5 = just the shared library, NOT the full development headers/compiler.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the already-installed Python packages from Stage 1.
# We are NOT re-running "pip install" here - we're copying the finished
# result, so this stage never needs gcc at all.
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Create a dedicated non-root user to run the app.
# Security best practice: if this container is ever compromised, the
# attacker doesn't get root access inside the container.
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy our actual application code into the image.
# We copy specific folders (not "COPY . ." for everything) so that things
# like venv/, tests/, .env, .git never end up inside the image.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Copy the startup script (see entrypoint.sh - it runs migrations, then
# starts the actual server).
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
# chmod +x makes the script executable - without this, Docker can't run it.

# Give our non-root user ownership of everything we just copied in.
RUN chown -R appuser:appuser /app

# Switch from root to our non-root user for everything from here on.
USER appuser

# Document which port this container listens on.
# NOTE: this line is informational only - it does NOT actually publish the
# port to your host machine. That happens separately, in docker-compose.yml
# via the "ports:" setting.
EXPOSE 8001

# HEALTHCHECK: Docker runs this command automatically every 10 seconds to
# check "is this service actually working?" If it fails 5 times in a row,
# Docker marks the container "unhealthy" - useful for docker-compose's
# "depends_on: condition: service_healthy" and, later, for Kubernetes probes.
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# This is the ONE AND ONLY main command - what actually runs when the
# container starts. It runs entrypoint.sh, which applies database
# migrations FIRST, then starts the real web server (uvicorn) SECOND.
# See entrypoint.sh in this same folder for the exact two steps.
CMD ["./entrypoint.sh"]
