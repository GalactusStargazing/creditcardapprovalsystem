# Credit Card Approval System

A cloud-native, microservices-based credit card approval platform built with FastAPI, Angular, and PostgreSQL. Deployed on AWS EKS with Prometheus/Grafana monitoring and automatic scaling.

![Architecture Diagram](./ARCHITECTURE.md)

**Live Demo**: https://dpscx2hwyvrkj.cloudfront.net

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Kubernetes Deployment](#kubernetes-deployment)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Credit Application Management**: Create, track, and manage credit card applications
- **Intelligent Credit Scoring**: Real-time credit decision engine with configurable scoring rules
- **Stateless Authorization**: Independent JWT verification across services
- **Database-per-Service**: Isolated databases for scalability and independent deployments
- **High Availability**: Multi-zone deployment with auto-scaling on AWS EKS
- **Real-time Monitoring**: Prometheus metrics and Grafana dashboards
- **Async Processing**: Non-blocking I/O with async/await throughout
- **OpenTelemetry Integration**: Distributed tracing across services
- **Graceful Failure Handling**: Timeout-aware service calls with honest error responses

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS CloudFront (CDN)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│                    AWS WAF                                   │
│         (Security rules & DDoS protection)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              AWS Network Load Balancer                       │
│              (TCP 80/443 port forwarding)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼──────────┐        ┌────────▼──────────┐
│   Worker Node 1  │        │   Worker Node 2   │
│ ┌──────────────┐ │        │ ┌──────────────┐  │
│ │ingress-nginx │ │        │ │ingress-nginx │  │
│ │(DaemonSet)   │ │        │ │(DaemonSet)   │  │
│ └──────────────┘ │        │ └──────────────┘  │
│ ┌──────────────┐ │        │ ┌──────────────┐  │
│ │Frontend Pod  │ │        │ │Frontend Pod  │  │
│ │Frontend Pod  │ │        │ │Frontend Pod  │  │
│ └──────────────┘ │        │ └──────────────┘  │
│ ┌──────────────┐ │        │ ┌──────────────┐  │
│ │Auth Service  │ │        │ │Auth Service  │  │
│ │Auth Pods     │ │        │ │Auth Pods     │  │
│ └──────────────┘ │        │ └──────────────┘  │
│ ┌──────────────┐ │        │ ┌──────────────┐  │
│ │App Service   │ │        │ │App Service   │  │
│ │App Pods      │ │        │ │App Pods      │  │
│ └──────────────┘ │        │ └──────────────┘  │
│ ┌──────────────┐ │        │ ┌──────────────┐  │
│ │Decision Svc  │ │        │ │Decision Svc  │  │
│ │Decision Pods │ │        │ │Decision Pods │  │
│ └──────────────┘ │        │ └──────────────┘  │
└──────────────────┘        └───────────────────┘
        │                             │
        └──────────────┬──────────────┘
                       │
         ┌─────────────▼─────────────┐
         │   PostgreSQL RDS Multi-AZ │
         │  ┌──────────────────────┐ │
         │  │ auth_db              │ │
         │  │ application_db       │ │
         │  │ decision_db          │ │
         │  └──────────────────────┘ │
         │  EBS Snapshots (automated)│
         └──────────────────────────┘
         
         ┌──────────────────────────────┐
         │  Monitoring & Observability  │
         │  ┌──────────────────────────┐│
         │  │   Prometheus             ││
         │  │   Grafana Dashboard      ││
         │  │   CloudWatch Metrics     ││
         │  │   OpenTelemetry Collector││
         │  └──────────────────────────┘│
         └──────────────────────────────┘
```

### Service Interaction Flow

1. **User Access**: Users access the application via CloudFront URL
2. **Security Layers**: AWS WAF inspects and filters requests
3. **Load Balancing**: NLB distributes traffic to EKS nodes
4. **Ingress Controller**: nginx-ingress routes traffic to appropriate services
5. **Microservices**: Three independent services process requests in parallel
6. **Data Layer**: PostgreSQL Multi-AZ ensures high availability

### Service Responsibilities

| Service | Purpose | Database | Port |
|---------|---------|----------|------|
| **Auth Service** | User registration, login, token generation | `auth_db` | 8001 |
| **Application Service** | Manage credit applications, coordinate decisions | `application_db` | 8002 |
| **Decision Service** | Credit scoring and decision logic | `decision_db` | 8003 |
| **Frontend** | Angular UI, handles routing and display | None | 80/443 |

### Database Schema (Simplified)

```sql
-- auth_db
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  full_name VARCHAR(255),
  password_hash VARCHAR(255),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- application_db
CREATE TABLE applications (
  id UUID PRIMARY KEY,
  user_id UUID,
  status VARCHAR(50), -- SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED
  monthly_income DECIMAL,
  credit_score INTEGER,
  employment_type VARCHAR(50),
  existing_loan_amount DECIMAL,
  card_number VARCHAR(20), -- Generated on approval
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- decision_db
CREATE TABLE decision_history (
  id UUID PRIMARY KEY,
  application_id UUID,
  decision VARCHAR(50), -- APPROVED, REJECTED
  score INTEGER,
  reasoning TEXT,
  created_at TIMESTAMP
);
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.141.1
- **Server**: Uvicorn 0.30.6
- **Database**: PostgreSQL 16 + SQLAlchemy ORM
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT), bcrypt
- **Validation**: Pydantic v2
- **Async Driver**: asyncpg
- **Testing**: pytest + pytest-asyncio
- **Monitoring**: Prometheus FastAPI Instrumentator, OpenTelemetry

### Frontend
- **Framework**: Angular 22.1.0
- **UI Components**: Angular Material 22.1.0
- **HTTP Client**: Angular HttpClient
- **Routing**: Angular Router
- **Package Manager**: npm 10.9.8
- **Linting**: ESLint + Prettier
- **Testing**: Vitest 4.0.8

### Infrastructure
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (EKS)
- **Ingress Controller**: nginx-ingress
- **Load Balancer**: AWS Network Load Balancer
- **CDN**: AWS CloudFront
- **WAF**: AWS WAF
- **Database Service**: AWS RDS PostgreSQL (Multi-AZ)
- **Storage**: EBS Volumes + EBS Snapshots
- **Monitoring**: Prometheus + Grafana
- **Tracing**: OpenTelemetry + OTLP Exporter
- **IaC**: Kubernetes YAML manifests
- **CI/CD**: GitHub Actions (config in `.github/workflows/`)

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose
- Node.js 20+ (for frontend local development)
- Python 3.10+ (for backend local development)

### Run with Docker Compose (Fastest)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/creditcardapprovalsystem.git
cd creditcardapprovalsystem

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your values (especially JWT_SECRET_KEY)

# 3. Start all services
docker-compose up -d

# 4. Wait for services to be healthy
docker-compose ps

# 5. Access the application
Frontend:  http://localhost:4200
Auth API:  http://localhost:8001/docs
App API:   http://localhost:8002/docs
Decision:  http://localhost:8003/docs
```

### Verify Services Are Running

```bash
# All services should return 200 OK
curl http://localhost:8001/health   # Auth Service
curl http://localhost:8002/health   # Application Service
curl http://localhost:8003/health   # Decision Service
```

### Create a Test User

```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

---

## 🏢 Local Development

### Backend Setup (FastAPI Services)

```bash
# Auth Service
cd auth-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start service
uvicorn app.main:app --reload --port 8001

# Run tests
pytest -v

# Deactivate
deactivate
```

Repeat for `application-service/` (port 8002) and `credit-decision-service/` (port 8003).

### Frontend Setup (Angular)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Access at http://localhost:4200

# Run tests
npm test

# Build for production
npm run build

# Lint and fix code
npm run lint:fix
```

### Database Setup (PostgreSQL)

```bash
# Start PostgreSQL (ensure docker-compose is running)
# Or use local PostgreSQL:

# Create databases
psql -U postgres -c "CREATE DATABASE auth_db;"
psql -U postgres -c "CREATE DATABASE application_db;"
psql -U postgres -c "CREATE DATABASE decision_db;"

# Run migrations for each service
cd auth-service && alembic upgrade head
cd ../application-service && alembic upgrade head
cd ../credit-decision-service && alembic upgrade head
```

### API Testing

Each service has interactive API documentation available at `/docs`:

- **Auth Service**: http://localhost:8001/docs
- **Application Service**: http://localhost:8002/docs
- **Decision Service**: http://localhost:8003/docs

Use these Swagger UIs to test endpoints interactively.

---

## 🎯 Kubernetes Deployment

### Prerequisites

```bash
# Install if not already present
docker --version          # Docker
kubectl version --client  # Kubernetes CLI
kind version              # Local cluster tool (or use EKS)
helm version              # Package manager (optional)
```

### Step 1: Create a Local Kubernetes Cluster (Development)

```bash
# Using kind for local testing
kind create cluster --name credit-card-app-cluster

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Step 2: Install Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### Step 3: Create Secrets (from `.example` templates)

```bash
# Copy and edit secret templates
cp k8s/postgres/secret.yaml.example k8s/postgres/secret.yaml
cp k8s/auth/secret.yaml.example k8s/auth/secret.yaml
cp k8s/application/secret.yaml.example k8s/application/secret.yaml

# Edit files with real values - CRITICAL: JWT_SECRET_KEY must be identical
# in auth/secret.yaml and application/secret.yaml
```

### Step 4: Deploy Services (in order)

```bash
# Namespace + PostgreSQL
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl get pods -n credit-card-app -w

# Auth Service (wait for postgres to be 1/1 Running)
kubectl apply -f k8s/auth/
kubectl get pods -n credit-card-app -w

# Application Service
kubectl apply -f k8s/application/
kubectl get pods -n credit-card-app -w

# Decision Service
kubectl apply -f k8s/decision/
kubectl get pods -n credit-card-app -w

# Frontend
kubectl apply -f k8s/frontend/
kubectl get pods -n credit-card-app -w

# Ingress (routing layer)
kubectl apply -f k8s/ingress/
kubectl get ingress -n credit-card-app
```

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n credit-card-app

# Expected output:
# postgres-0              1/1 Running
# auth-xxxxx              1/1 Running
# application-xxxxx       1/1 Running
# decision-xxxxx          1/1 Running
# frontend-xxxxx          1/1 Running
```

### Step 6: Access the Application

```bash
# Forward ingress port
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8888:80

# Access at http://localhost:8888
```

### AWS EKS Deployment

For production on AWS EKS:

```bash
# 1. Create EKS cluster (using AWS CLI or AWS Console)
# 2. Configure kubectl context
aws eks update-kubeconfig --name credit-card-app --region us-east-1

# 3. Install AWS Load Balancer Controller
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system

# 4. Deploy services (same as above)
kubectl apply -f k8s/

# 5. Get load balancer endpoint
kubectl get ingress -n credit-card-app
# Use the EXTERNAL-IP provided
```

### Helm Charts (Optional)

Alternatively, deploy using Helm:

```bash
# Create release
helm install credit-card-app ./helm-charts/credit-card-app \
  -n credit-card-app \
  --create-namespace

# Upgrade release
helm upgrade credit-card-app ./helm-charts/credit-card-app \
  -n credit-card-app

# Check status
helm status credit-card-app -n credit-card-app
```

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

# Response 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2026-08-23T10:30:00Z"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}

# Response 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "full_name": "John Doe"
  }
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer {access_token}

# Response 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "full_name": "John Doe"
}
```

### Application Endpoints

#### Create Application
```http
POST /applications
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "monthly_income": 75000,
  "credit_score": 720,
  "employment_type": "salaried",
  "existing_loan_amount": 150000
}

# Response 201 Created
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "UNDER_REVIEW",
  "monthly_income": 75000,
  "credit_score": 720,
  "employment_type": "salaried",
  "existing_loan_amount": 150000,
  "card_number": null,
  "created_at": "2026-08-23T10:35:00Z"
}
```

#### List User's Applications
```http
GET /applications
Authorization: Bearer {access_token}

# Response 200 OK
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "status": "APPROVED",
    "card_number": "4532-1234-5678-9101",
    "created_at": "2026-08-23T10:35:00Z"
  }
]
```

#### Get Application Details
```http
GET /applications/{application_id}
Authorization: Bearer {access_token}

# Response 200 OK
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "APPROVED",
  "monthly_income": 75000,
  "credit_score": 720,
  "employment_type": "salaried",
  "existing_loan_amount": 150000,
  "card_number": "4532-1234-5678-9101",
  "created_at": "2026-08-23T10:35:00Z",
  "updated_at": "2026-08-23T10:36:00Z"
}
```

#### Get Application Status
```http
GET /applications/{application_id}/status
Authorization: Bearer {access_token}

# Response 200 OK
{
  "status": "APPROVED",
  "decision": {
    "score": 95,
    "decision": "APPROVED",
    "reasoning": "Excellent credit profile"
  }
}
```

### Credit Decision Endpoints

#### Evaluate Application
```http
POST /decisions/evaluate
Content-Type: application/json

{
  "monthly_income": 75000,
  "credit_score": 720,
  "employment_type": "salaried",
  "existing_loan_amount": 150000
}

# Response 200 OK
{
  "score": 95,
  "decision": "APPROVED",
  "reasoning": "Strong financial profile: excellent credit score, stable income, low debt ratio"
}
```

#### Get Decision History
```http
GET /decisions/history/{application_id}

# Response 200 OK
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "application_id": "660e8400-e29b-41d4-a716-446655440001",
    "decision": "APPROVED",
    "score": 95,
    "reasoning": "Strong financial profile",
    "created_at": "2026-08-23T10:36:00Z"
  }
]
```

### Health Check Endpoints

```bash
# Each service exposes a health endpoint
GET /health

# Response 200 OK
{
  "status": "ok",
  "service": "auth-service",
  "db": "connected"
}
```

---

## 🗄️ Database Schema

### Users Table (`auth_db`)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

### Applications Table (`application_db`)
```sql
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED',
  monthly_income DECIMAL(15,2),
  credit_score INTEGER,
  employment_type VARCHAR(50),
  existing_loan_amount DECIMAL(15,2),
  card_number VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
```

### Decision History Table (`decision_db`)
```sql
CREATE TABLE decision_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL,
  decision VARCHAR(50) NOT NULL,
  score INTEGER NOT NULL,
  reasoning TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_decision_history_application_id ON decision_history(application_id);
```

---

## 🧪 Testing

### Unit & Integration Tests

```bash
# Auth Service
cd auth-service
pytest -v                    # Run all tests
pytest tests/test_auth.py -v # Specific test file
pytest -v --cov              # With coverage report

# Application Service
cd ../application-service
pytest -v
pytest tests/test_applications.py::test_create_application -v

# Decision Service
cd ../credit-decision-service
pytest -v
```

### Frontend Tests

```bash
cd frontend
npm test                     # Run all tests
npm test -- --run            # Single run (CI mode)
npm test src/app/pages/login/login.ts  # Specific file
```

### Load Testing (K6 - optional)

```bash
# Install k6
# https://k6.io/docs/get-started/installation/

k6 run ./load-test.js        # Run load test
```

### End-to-End Tests (Cypress - optional)

```bash
cd frontend
npm install --save-dev cypress
npx cypress open              # Interactive testing
npx cypress run               # Headless testing
```

---

## 📊 Monitoring

### Prometheus Metrics

Each FastAPI service exposes Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8001/metrics
curl http://localhost:8002/metrics
curl http://localhost:8003/metrics
```

### Grafana Dashboards

Access Grafana (if running in K8s):

```bash
# Port-forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access at http://localhost:3000
# Default credentials: admin / prom-operator
```

### OpenTelemetry Traces

Services send traces to an OpenTelemetry collector. To view traces:

1. Set up Jaeger or Tempo
2. Configure collector endpoint in `.env` or K8s ConfigMap
3. Access Jaeger UI for trace exploration

### Key Metrics to Monitor

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `http_request_duration_seconds` | Request latency | > 1000ms (p99) |
| `http_requests_total` | Total requests | Baseline + 50% |
| `database_connection_errors` | DB connection failures | > 0 |
| `application_submitted_total` | Applications created | Baseline for anomaly detection |
| `application_approved_total` | Approved applications | Track approval rate |
| `credit_decision_latency` | Decision service response time | > 500ms (p99) |

---

## 🔒 Security

### Best Practices Implemented

1. **Password Security**: bcrypt hashing with salt
2. **JWT Authentication**: Stateless, time-limited tokens (60 min default)
3. **Authorization**: Role-based checks (JWT claims)
4. **Input Validation**: Pydantic schema validation on all endpoints
5. **Database Security**: 
   - Parameterized queries (SQLAlchemy)
   - Separate databases per service
   - Connection pooling
6. **Infrastructure Security**:
   - AWS WAF for DDoS/bot protection
   - Network security groups / K8s NetworkPolicies
   - TLS encryption in transit (CloudFront, NLB)
7. **Secrets Management**:
   - Environment variables (never in code)
   - AWS Secrets Manager (production)
   - Gitignored `.env` and `secret.yaml` files

### Environment Variables (Keep Secure)

Never commit real values. Use:
- `.env` file (local development, gitignored)
- GitHub Secrets (CI/CD)
- AWS Secrets Manager (production K8s)
- K8s Secrets (deployed apps)

---

## 📝 Contributing

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes** and test locally
   ```bash
   # Test backend
   cd auth-service && pytest -v
   
   # Test frontend
   cd ../frontend && npm test
   ```

3. **Commit with Clear Messages**
   ```bash
   git add .
   git commit -m "feat: add credit score weight adjustment"
   ```

4. **Push to GitHub**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** on GitHub
   - Describe what changed and why
   - Link related issues
   - Ensure CI checks pass

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **TypeScript**: ESLint + Prettier (run `npm run lint:fix`)
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)
- **Tests**: Maintain > 80% coverage

### Reporting Issues

Use GitHub Issues with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, versions, etc.)

---

## 🛠️ Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs auth-service
kubectl logs deployment/auth -n credit-card-app

# Common issues:
# 1. Database not ready: wait 10-15s, retry
# 2. Port already in use: change PORT in .env
# 3. Database URL wrong: verify credentials and host
```

### JWT Token Issues

```bash
# Token expired: login again
# Token invalid: ensure JWT_SECRET_KEY matches across services
# Check JWT decode:
python -c "import jwt; print(jwt.decode('your_token', 'your_secret', algorithms=['HS256']))"
```

### Database Connection Errors

```bash
# Verify PostgreSQL is running
docker-compose ps db

# Check connection
psql -U ccapp -d auth_db -h localhost

# Run migrations
cd auth-service && alembic upgrade head
```

### Kubernetes Pod Stuck in CrashLoopBackOff

```bash
# Check pod logs
kubectl describe pod <pod-name> -n credit-card-app
kubectl logs <pod-name> -n credit-card-app

# Common causes:
# 1. Secret not created: verify secret.yaml exists and is valid
# 2. Database not ready: check postgres-0 pod
# 3. Service DNS not resolving: verify fully-qualified names in nginx.conf
```

---

## 📚 Documentation

- **[Architecture Deep Dive](./ARCHITECTURE.md)**: Service interactions, scoring rules, failure handling
- **[Kubernetes Setup Guide](./K8s/SETUP.md)**: Step-by-step K8s deployment on kind or EKS
- **[API Swagger Docs](./API_DOCS.md)**: Full endpoint reference with request/response examples

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👥 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/creditcardapprovalsystem/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/creditcardapprovalsystem/discussions)
- **Email**: support@creditcardapp.example.com

---

## 🙋 Frequently Asked Questions

**Q: Can I run this locally without Kubernetes?**  
A: Yes! Use `docker-compose up` for local development. Kubernetes is for production on EKS.

**Q: How do I scale the services?**  
A: Edit K8s deployments to increase replicas, or enable Horizontal Pod Autoscaler (HPA). Metrics are scraped by Prometheus for autoscaling decisions.

**Q: What's the approval rate in production?**  
A: Check Grafana dashboard "Application Metrics" panel. Track with `application_approved_total` metric.

**Q: How do I integrate my own credit bureau API?**  
A: Modify `credit-decision-service/app/services/` and add API calls within the scoring logic.

**Q: Is PCI-DSS compliance included?**  
A: Card generation is mocked (`generate_card_number()`). For real cards, integrate with payment processors (Stripe, Square) that handle PCI compliance.

---

**Last Updated**: August 2026  
**Version**: 1.0.0  
**Maintainer**: Development Team
