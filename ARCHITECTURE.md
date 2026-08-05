# Architecture

## Service Overview

```mermaid
graph TD
    A[Angular Frontend<br/>localhost:4200] -->|REST/JSON| B[Auth Service<br/>localhost:8001]
    A -->|REST/JSON + JWT| C[Application Service<br/>localhost:8002]
    C -->|REST/JSON<br/>internal call| D[Credit Decision Service<br/>localhost:8003]

    B --> B1[(auth_db)]
    C --> C1[(application_db)]
    D --> D1[(decision_db)]

    style B fill:#1e3a5f,color:#fff
    style C fill:#1e3a5f,color:#fff
    style D fill:#1e3a5f,color:#fff
```

## Database-per-Service

```mermaid
graph TD
    subgraph PG["Single PostgreSQL Server (local dev)"]
        AuthDB[(auth_db)]
        AppDB[(application_db)]
        DecDB[(decision_db)]
    end

    AuthSvc[Auth Service] -->|owns, full access| AuthDB
    AppSvc[Application Service] -->|owns, full access| AppDB
    DecSvc[Credit Decision Service] -->|owns, full access| DecDB

    AppSvc -.->|never direct DB access| DecDB
    AppSvc -.->|never direct DB access| AuthDB
    DecSvc -.->|never direct DB access| AppDB
```

Each service only ever queries its own database. Cross-service data needs go through REST APIs, never direct DB access — this is what makes each service independently deployable and testable.

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as Angular
    participant Auth as Auth Service :8001
    participant AuthDB as auth_db

    U->>Auth: POST /auth/register
    Auth->>Auth: hash password (bcrypt)
    Auth->>AuthDB: INSERT user
    Auth-->>U: 201 Created

    U->>Auth: POST /auth/login
    Auth->>AuthDB: verify credentials
    Auth->>Auth: generate JWT {user_id}
    Auth-->>U: 200 OK {access_token}

    U->>Auth: GET /auth/me (Bearer token)
    Auth->>Auth: decode & verify JWT
    Auth-->>U: current user info
```

**Key point**: Application Service verifies the same JWT independently using a shared `JWT_SECRET_KEY` — it never calls Auth Service to check token validity. This is stateless authentication: less coupling, but no instant token revocation.

## Application → Decision Flow

```mermaid
sequenceDiagram
    participant U as Angular
    participant App as Application Service :8002
    participant AppDB as application_db
    participant Dec as Credit Decision Service :8003
    participant DecDB as decision_db

    U->>App: POST /applications (JWT + form data)
    App->>App: verify JWT independently
    App->>AppDB: INSERT application, status=SUBMITTED
    App->>AppDB: UPDATE status=UNDER_REVIEW

    App->>Dec: POST /decisions/evaluate
    Dec->>Dec: score application (0-100)
    Dec->>DecDB: INSERT decision_history
    Dec-->>App: {score, decision, reason}

    App->>AppDB: UPDATE status = APPROVED/REJECTED<br/>(+ generate card_number if approved)
    App-->>U: final application state
```

## Failure Handling

```mermaid
sequenceDiagram
    participant U as Angular
    participant App as Application Service
    participant Dec as Credit Decision Service (down)

    U->>App: POST /applications
    App->>AppDB: save, status=UNDER_REVIEW
    App->>Dec: POST /decisions/evaluate (5s timeout)
    Dec--xApp: connection refused / timeout
    App-->>U: 503 - "saved and under review"
```

No retries or circuit breakers (deliberately out of scope for this phase) — a downstream failure is caught, the application data isn't lost, and the user gets an honest error instead of a crash.

## Scoring Rules (Credit Decision Service)

| Rule | Condition | Points |
|---|---|---|
| Credit score | ≥ 700 | +30 |
| Monthly income | ≥ ₹50,000 | +30 |
| Existing loan | < ₹200,000 | +20 |
| Employment | Salaried | +20 |
| Employment | Other | +10 |

**Score ≥ 80 → APPROVED, otherwise REJECTED**
