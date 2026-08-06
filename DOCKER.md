# Docker Guide — Credit Card Approval System

This document explains **what Docker actually does in this project, and why**, for anyone on the team who hasn't worked with Docker before. If you just want to run the project, see the "Quick Start with Docker" section in `README.md` instead — this file is for understanding, not for running commands.

---

## The Problem Docker Solves Here

Before Docker, running this whole system required:
- Installing Python 3.12, creating 3 separate virtual environments
- Installing PostgreSQL and manually creating 3 databases
- Installing Node.js and Angular CLI
- Running 4 separate terminal windows, each with its own long command

Every teammate would have to repeat all of that, and small differences (a different Python version, a missing system library) could cause "works on my machine" bugs.

**Docker packages each service into a self-contained box (called an image)** that includes everything it needs to run — the code, the Python interpreter, the exact library versions — so it behaves identically on any machine.

**Docker Compose then starts all these boxes together**, wired up so they can talk to each other, with a single command.

---

## Two Different Files: Dockerfile vs docker-compose.yml

These serve completely different purposes and are easy to confuse at first.

### `Dockerfile` (one per service) — "How do I BUILD this one service into an image?"

Each service (`auth-service/`, `application-service/`, `credit-decision-service/`, `frontend/`) has its own `Dockerfile`. It's a step-by-step recipe: start from a base image, install dependencies, copy in the code, define how to start it.

### `docker-compose.yml` (one, at the project root) — "How do I RUN all these images TOGETHER?"

This file doesn't build anything itself — it references each service's `Dockerfile`, plus adds a PostgreSQL database, and describes:
- What environment variables each service needs
- Which ports to expose
- What order things should start in (database first, then services, then frontend)
- How services should find each other (by name, e.g. `auth-service`, not by IP address)

**Analogy:** a `Dockerfile` is a recipe for baking one cake. `docker-compose.yml` is the instructions for serving an entire multi-course meal, where some dishes need to be ready before others.

---

## Why Every Backend Dockerfile Has Two "Stages"

Open any of the 3 Python service Dockerfiles and you'll see two `FROM python:3.12-slim` lines. This is called a **multi-stage build**.

**The problem:** some Python packages (`asyncpg` for talking to PostgreSQL, `bcrypt` for password hashing) need a C compiler (`gcc`) to install. But that compiler is only needed *once*, during installation — the final running app never touches it again.

**The solution:** Stage 1 ("deps") installs everything, compiler included. Stage 2 ("runner") starts completely fresh and only copies over the *already-installed* packages — never the compiler itself. The result: a smaller, cleaner final image with less attack surface (fewer tools available if the container were ever compromised).

---

## Why the Frontend Dockerfile Looks So Different

The 3 backend services all run Python code directly (`uvicorn`, a web server, keeps running forever, handling requests).

The frontend is different: Angular code gets **compiled** into plain HTML/CSS/JS files (this is what `ng build` does). Once that's done, there's no "Angular process" to keep running — you just need *something* to hand those files to a browser.

That's why the frontend Dockerfile's two stages do genuinely different jobs:
- **Stage 1** uses Node.js just to run `ng build` and produce the static files
- **Stage 2** throws Node.js away entirely and uses **Nginx** (a lightweight web server) to serve those files instead

This is also why the frontend's final image is tiny (~50MB) compared to the backend services (~200-250MB each) — there's no programming language runtime in the final frontend image at all, just static files and a web server.

---

## What is Nginx, and Why Do We Need It?

Nginx does **two jobs** in this project:

**1. Serving static files** — handing the built Angular app to the browser when you visit `http://localhost:4200`.

**2. Reverse proxy** — when the Angular app (running in your browser) needs to call the Auth Service, it can't reach `auth-service:8001` directly — that hostname only exists *inside* Docker's internal network, which your browser has no access to. So the browser calls `http://localhost:4200/api/v1/auth/login` instead, and Nginx secretly forwards that request to the real `auth-service` container behind the scenes.

Browser Nginx (in frontend container) Auth Service container
| | |
| GET localhost:4200/api/v1/auth/... | |
|----------------------------------->| |
| | forwards to auth-service:8001|
| |----------------------------->|
| | response |
| |<-----------------------------|
| response | |
|<-----------------------------------| |


This routing logic lives in `frontend/nginx.conf`.

---

## Why `entrypoint.sh` Instead of Starting the Server Directly

Each backend service's Dockerfile ends with `CMD ["./entrypoint.sh"]` instead of directly running `uvicorn`. `entrypoint.sh` does two things in order:

```bash
alembic upgrade head       # 1. Apply any pending database schema changes
exec uvicorn app.main:app  # 2. THEN start the actual web server
```

This means database migrations happen **automatically** every time a container starts — nobody on the team needs to remember a manual migration step.

---

## Why Containers Talk to Each Other by Name, Not IP Address

Inside `docker-compose.yml`, you'll see things like:
```yaml
CREDIT_DECISION_SERVICE_URL: http://decision-service:8003
```

`decision-service` isn't a real domain name on the internet — it's the **service name** defined in `docker-compose.yml`. Docker Compose automatically creates a private network where every container can find every other container just by its service name, similar to how your computer resolves `google.com` to an IP address, but entirely private to this project.

This matters because IP addresses can change every time a container restarts, but service names stay constant — so hardcoding an IP address would break unpredictably, while the name-based approach never does.

---

## Debugging Lessons From Building This (Real Issues We Hit)

Worth knowing these exist, since they're realistic Docker/Nginx gotchas, not mistakes unique to this project:

**1. Permission denied running the app as a non-root user**
Installing Python packages with `pip install --user` put them inside `/root/`, a directory only the `root` user can access — but we deliberately run the app as a non-root `appuser` for security. Fix: install packages to a normal shared location (`/usr/local/`) instead.

**2. Nginx returning 404 "Not Found" for real endpoints**
When `proxy_pass` uses a variable (which we need, for reasons below), Nginx's usual automatic path-forwarding stops working — it was silently dropping part of the URL. Fix: explicitly forward the full original path using `$uri`.

**3. Why does `proxy_pass` even need a variable?**
By default, Nginx resolves hostnames like `auth-service` once, when it starts. If `auth-service`'s container isn't running yet at that moment, Nginx would crash immediately on startup. Using a variable makes Nginx resolve the hostname *per request* instead, so the frontend container can start even before the backend containers exist — important for correct startup ordering.

**4. Frontend showing "unhealthy" despite working fine in the browser**
Alpine Linux's `wget` sometimes tries IPv6 (`::1`) first when resolving `localhost`, where nothing is listening. Fix: use `127.0.0.1` explicitly in healthchecks instead of `localhost`.

**5. A healthcheck fix that didn't seem to take effect**
`docker-compose.yml` can define its own `healthcheck:` per service, which **always overrides** whatever `HEALTHCHECK` is written in that service's Dockerfile. We'd fixed the Dockerfile correctly, but the actual override lived in `docker-compose.yml` and needed the same fix applied there too.

---

## Quick Reference: Every Docker-Related File in This Repo

docker-compose.yml → Orchestrates all 5 containers together
.env / .env.example → Shared config (passwords, secrets, ports) for Compose
db/init.sql → Creates the 3 databases inside the PostgreSQL container

auth-service/
Dockerfile → How to build the Auth Service image
entrypoint.sh → What runs when the container starts (migrate, then serve)
.dockerignore → Files to exclude from the image (venv/, .env, tests/)

application-service/ → Same 3 files, for Application Service
credit-decision-service/ → Same 3 files, for Credit Decision Service

frontend/
Dockerfile → How to build the frontend image (Node build → Nginx serve)
nginx.conf → Routing rules: serve static files + proxy API calls
.dockerignore → Files to exclude (node_modules/, dist/)
