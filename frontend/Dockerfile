# =============================================================================
# FRONTEND - Dockerfile
# =============================================================================
# This builds a container image for the Angular frontend. Unlike the backend
# services, this is NOT a Python app - it's a two-stage build where:
#
#   Stage 1 uses Node.js to COMPILE the Angular app into plain static files
#            (HTML, JS, CSS). Once done, Node.js is no longer needed at all.
#
#   Stage 2 uses Nginx (a lightweight web server) to SERVE those static
#            files, and to forward ("proxy") API calls to the correct
#            backend service.
#
# The final image contains ZERO Node.js - it's thrown away after Stage 1,
# which is why this image is only ~50MB, versus ~200MB+ for the Python
# services.
# =============================================================================


# =============================================================================
# STAGE 1: "builder" - compiles the Angular app into static files
# =============================================================================
FROM node:22-alpine AS builder
# node:22-alpine = Node.js 22 on a minimal Alpine Linux base.
# Alpine is fine here (unlike the Python services) because Node's build
# tools don't have the same C-library compatibility issues that broke
# Python's asyncpg/bcrypt packages.

WORKDIR /app

# Copy only package.json/package-lock.json first (same caching trick as
# the Python services' requirements.txt) - if dependencies haven't changed,
# Docker reuses the cached "npm install" instead of re-running it.
COPY package*.json ./
RUN npm install

# Now copy the actual source code and build it.
COPY . .
RUN npm run build
# "npm run build" runs "ng build", which compiles all the TypeScript/HTML/
# SCSS into plain static files, output to dist/frontend/browser/.
# It uses environment.prod.ts (not environment.ts) automatically, because
# of the "fileReplacements" config in angular.json - this swaps in relative
# "/api/v1" URLs instead of hardcoded "localhost:8001" URLs, since in this
# containerized setup, Nginx (not the browser) handles routing to backends.


# =============================================================================
# STAGE 2: "runner" - this becomes the ACTUAL final image
# =============================================================================
FROM nginx:1.27-alpine AS runner
# A minimal Nginx web server image. Nginx's only two jobs here are:
#   1. Serve the built Angular files to the browser
#   2. Forward API requests (e.g. /api/v1/auth/login) to the right backend
#      container, since the browser itself cannot reach Docker's internal
#      network directly.

# Copy ONLY the compiled static files from Stage 1 - nothing else from
# Stage 1 (no node_modules, no TypeScript source, no Node.js itself)
# makes it into this final image.
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html

# Copy our custom Nginx configuration, which defines the routing rules
# (see nginx.conf in this same folder for the full explanation).
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx listens on port 80 inside the container (mapped to 4200 on your
# host machine via docker-compose.yml).
EXPOSE 80

# Periodic check: is Nginx actually responding?
# NOTE: we use 127.0.0.1 here specifically (not "localhost") because
# Alpine's wget sometimes resolves "localhost" to IPv6 (::1) first, where
# nothing is listening, causing false "unhealthy" reports. 127.0.0.1 avoids
# that ambiguity entirely.
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD wget -qO- http://127.0.0.1:80/health || exit 1

# The ONE main command: start Nginx.
# "-g daemon off" keeps Nginx running in the FOREGROUND. This matters
# because Docker needs the main process to stay in the foreground to know
# the container is still alive - if Nginx backgrounded itself (its normal
# default behavior), Docker would think the container exited immediately.
CMD ["nginx", "-g", "daemon off;"]
