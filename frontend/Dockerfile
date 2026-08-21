# =============================================================================
# FRONTEND - Dockerfile
# =============================================================================

# =============================================================================
# STAGE 1: "builder" - compile Angular application
# =============================================================================
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build


# =============================================================================
# STAGE 2: "runner" - serve Angular using Nginx
# =============================================================================
FROM nginx:1.27-alpine AS runner

# Update Alpine packages to the latest security patches
RUN apk update && \
    apk upgrade --no-cache

# Copy Angular production build
COPY --from=builder /app/dist/frontend/browser /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Container health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
    CMD wget -qO- http://127.0.0.1:80/health || exit 1

# Start Nginx in foreground
CMD ["nginx", "-g", "daemon off;"]
