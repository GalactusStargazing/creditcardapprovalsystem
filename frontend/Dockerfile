# =============================================================================
# FRONTEND - Dockerfile
# =============================================================================
# Two-stage Angular build:
#
# Stage 1 -> Node.js builds the Angular application
# Stage 2 -> Nginx serves the compiled static files
#
# Node.js and node_modules do NOT exist in the final image.
# =============================================================================


# =============================================================================
# STAGE 1: "builder" - builds the Angular application
# =============================================================================

FROM node:22-alpine AS builder

WORKDIR /app

# Copy package files first for Docker layer caching
COPY package*.json ./

# Use npm ci for reproducible CI/CD builds
RUN npm ci

# Copy Angular source code
COPY . .

# Build Angular application
RUN npm run build


# =============================================================================
# STAGE 2: "runner" - final production image
# =============================================================================

FROM nginx:1.29-alpine AS runner

# Update Alpine packages to the latest available security patches
RUN apk update && apk upgrade --no-cache

# Copy ONLY the compiled Angular application
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx listens on port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD wget -qO- http://127.0.0.1:80/health || exit 1

# Keep Nginx running in the foreground
CMD ["nginx", "-g", "daemon off;"]
