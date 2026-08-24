# Credit Card Approval System — Microservices Learning Project

A full-stack credit card application system built to learn microservice architecture fundamentals: service boundaries, database-per-service, synchronous REST communication, and stateless JWT authentication across independently deployable services.

## Architecture

Angular (4200)
|
├── Auth Service (8001) ──────► auth_db
|
└── Application Service (8002) ──────► application_db
|
└── (HTTP) ──► Credit Decision Service (8003) ──► decision_db

Three independent FastAPI microservices, each with its own PostgreSQL database, own Alembic migration history, and own test suite. No service directly accesses another service's database — all cross-service communication happens over REST.

### Services

| Service | Port | Responsibility | Database |
|---|---|---|---|
| Auth Service | 8001 | User registration, login, JWT issuance | `auth_db` |
| Application Service | 8002 | Credit card applications, status tracking, calls Credit Decision Service | `application_db` |
| Credit Decision Service | 8003 | Scores applications and returns APPROVED/REJECTED | `decision_db` |
| Angular Frontend | 4200 | Customer-facing UI | — |

### Key design decisions

- **Database-per-service**: each service owns its data exclusively. `user_id` and `application_id` fields that reference other services' data are plain UUIDs, not foreign keys — cross-service joins are never done at the database level.
- **Stateless JWT verification**: Auth Service issues JWTs; Application Service independently verifies them using a shared secret (`JWT_SECRET_KEY`), with zero network calls back to Auth Service.
- **Synchronous REST over HTTP**: Application Service calls Credit Decision Service via `httpx`, with a timeout and graceful `503` handling if the decision service is unavailable — no message queues, no retries, by design (kept simple for this learning phase).

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, JWT (python-jose), bcrypt (passlib)
- **Frontend**: Angular 22, TypeScript, Angular Material, Reactive Forms, Signals
- **Testing**: pytest, pytest-asyncio, httpx

## Project Structure

credit-card-approval-system/
├── auth-service/
│ ├── app/
│ │ ├── api/routes/ # HTTP endpoints
│ │ ├── core/ # config, security (JWT, hashing)
│ │ ├── models/ # SQLAlchemy models
│ │ ├── schemas/ # Pydantic request/response schemas
│ │ ├── repositories/ # DB query layer
│ │ ├── services/ # business logic
│ │ └── db/ # session, base
│ ├── alembic/ # migrations
│ ├── tests/
│ └── requirements.txt
├── application-service/ # same structure as auth-service
├── credit-decision-service/ # same structure as auth-service
└── frontend/ # Angular app

## Quick Start with Docker (Recommended)

The fastest way to run the entire system — no Python, Node, or PostgreSQL installation required.

### Prerequisites
- Docker and Docker Compose installed ([Get Docker](https://docs.docker.com/get-docker/))

### Run everything with one command

```bash
git clone <this-repo-url>
cd credit-card-approval-system
cp .env.example .env
```

Edit `.env` and set:
- `POSTGRES_PASSWORD` — any strong password
- `JWT_SECRET_KEY` — generate one with:
```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then start everything:

```bash
docker compose up -d --build
```

This builds all 4 service images and starts Postgres + Auth Service + Application Service + Credit Decision Service + Angular frontend, wired together on a shared Docker network.

### Verify it's running

```bash
docker compose ps
```

All 5 containers should show `healthy` within about a minute. Then open:

http://localhost:4200

### Stopping

```bash
docker compose down          # stops containers, keeps data
docker compose down -v       # stops containers AND deletes all data
```

### Rebuilding after code changes

```bash
docker compose up -d --build
```

### Viewing logs

```bash
docker compose logs -f                      # all services
docker compose logs -f application-service  # just one service
```

### Architecture note

Database migrations run automatically on container startup (via each service's `entrypoint.sh`) — no manual `alembic upgrade head` step needed. Services communicate over Docker's internal network using service names (`auth-service`, `application-service`, `decision-service`, `db`), never hardcoded IPs or `localhost`.

---

## Manual Local Development Setup (without Docker)

The instructions below are for running each service individually with Python venvs and a locally-installed PostgreSQL — useful for active backend development and debugging with hot-reload.

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Node.js 22+ and Angular CLI
- `python3-venv` (`sudo apt install python3.12-venv` on Ubuntu)

## Setup

### 1. Database

```bash
sudo -u postgres psql
```
```sql
CREATE USER ccapp WITH PASSWORD 'your_password_here';
CREATE DATABASE auth_db OWNER ccapp;
CREATE DATABASE application_db OWNER ccapp;
CREATE DATABASE decision_db OWNER ccapp;
```

### 2. Each backend service (repeat for `auth-service`, `application-service`, `credit-decision-service`)

```bash
cd <service-name>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL / JWT_SECRET_KEY as needed
alembic upgrade head
```

**Important**: `JWT_SECRET_KEY` must be identical in `auth-service/.env` and `application-service/.env` — this is what allows Application Service to independently verify tokens issued by Auth Service.

### 3. Frontend

```bash
cd frontend
npm install
```

## Running Locally

Each service runs independently in its own terminal:

```bash
# Terminal 1
cd auth-service && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2
cd application-service && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 3
cd credit-decision-service && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 4
cd frontend && ng serve
```

Then open **http://localhost:4200**.

API docs (Swagger) available at:
- http://localhost:8001/docs
- http://localhost:8002/docs
- http://localhost:8003/docs

## Running Tests

```bash
cd <service-name>
source venv/bin/activate
pytest -v
```

Each service uses a dedicated `test_<service>_db` database (see `.env.test`), isolated from local development data.

## Application Flow

1. Customer registers → Auth Service creates user, hashes password
2. Customer logs in → Auth Service returns JWT
3. Customer submits a card application → Application Service verifies JWT, saves application (`SUBMITTED` → `UNDER_REVIEW`)
4. Application Service calls Credit Decision Service with income/credit score/loan/occupation
5. Credit Decision Service scores the application (0–100) and returns `APPROVED`/`REJECTED`
6. Application Service updates status; if approved, generates a 15-digit card number (prefix `3579`)
7. Customer views final status and (if approved) card number

### Credit scoring rules

| Rule | Condition | Points |
|---|---|---|
| Credit score | ≥ 700 | +30 |
| Monthly income | ≥ ₹50,000 | +30 |
| Existing loan amount | < ₹200,000 | +20 |
| Employment | Salaried / Other | +20 / +10 |

Score ≥ 80 → **APPROVED**, otherwise **REJECTED**.

## Known Limitations (by design, for this learning phase)

- No retry/circuit-breaker logic on inter-service calls
- No message queue / async event-driven communication
- Card number uniqueness relies on random generation without collision retry (acceptable at low volume)
- No admin role/dashboard — all users are customers

## Roadmap

- [x] Dockerize each service
- [x] Docker Compose for local orchestration
- [x] Kubernetes deployment
- [x] AWS EC2 hosting
- [x] Monitoring with Prometheus + Grafana
