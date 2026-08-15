# Local Setup Guide — Credit Card Approval System (Kubernetes / kind)

This guide walks through running the full system (PostgreSQL, Auth Service, Application Service, Credit Decision Service, Frontend, and Ingress) on a local Kubernetes cluster using `kind`.

Branch: `feature/test1` — rebuilt from scratch and verified end-to-end (see commit history for the specific bugs found and fixed: Postgres image version, missing `POSTGRES_DB`, Nginx DNS resolution).

---

## 1. Prerequisites

Check these are installed:

```bash
docker --version
kubectl version --client
kind version
```

If any are missing:

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/kubectl

# kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

---

## 2. Clone and check out the branch

```bash
git clone https://github.com/GalactusStargazing/creditcardapprovalsystem.git
cd creditcardapprovalsystem
git checkout feature/test1
```

---

## 3. Create the local kind cluster

```bash
kind create cluster --name credit-card-app-cluster
kubectl cluster-info --context kind-credit-card-app-cluster
kubectl get nodes
```

Expect one node, `STATUS: Ready`.

### Starting completely fresh (if you already have a cluster with old/broken state)

If you're re-running this after earlier experimentation and want a guaranteed clean slate:

```bash
kubectl delete namespace credit-card-app --ignore-not-found
kind delete cluster --name credit-card-app-cluster
kind create cluster --name credit-card-app-cluster
kubectl cluster-info --context kind-credit-card-app-cluster
kubectl get nodes
```

This removes both the app namespace and the entire cluster, then recreates the cluster from scratch — the same approach used to rebuild this branch cleanly.

---

## 4. Install the Ingress controller

`kind` does not bundle an Ingress controller by default — install the Nginx Ingress Controller:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

Verify:

```bash
kubectl get pods -n ingress-nginx
```

---

## 5. Create the real secret files

Real secrets are **gitignored** — every teammate creates their own `secret.yaml` locally from the committed `.example` templates:

```bash
cp k8s/postgres/secret.yaml.example k8s/postgres/secret.yaml
cp k8s/auth/secret.yaml.example k8s/auth/secret.yaml
cp k8s/application/secret.yaml.example k8s/application/secret.yaml
```

Edit each file and fill in real values.

**Critical — these values must be consistent across files:**

| Value | Must match in |
|---|---|
| `POSTGRES_PASSWORD` (postgres/secret.yaml) | The password embedded in `DATABASE_URL` in `auth/secret.yaml` **and** `application/secret.yaml` |
| `JWT_SECRET_KEY` | Must be **byte-for-byte identical** in `auth/secret.yaml` and `application/secret.yaml` |

Auth Service signs JWTs with this key; Application Service independently verifies them with it — if they don't match exactly, every login will appear to succeed but every authenticated request afterward will fail.

`decision/` has no `secret.yaml` — Credit Decision Service never handles passwords or JWTs.

### Getting the actual values

The real password and JWT secret used for local testing are **not** included in this document or committed to git. Ask in the team channel / DM whoever set up `feature/test1` for the current working values — they'll match the `secret.yaml.example` structure above exactly, just with real values in place of the placeholders.

---

## 6. Apply and verify — one service at a time

Apply in this order. Each service should reach `1/1 Running` before moving to the next, since later services depend on earlier ones.

### 6.1 Namespace + PostgreSQL

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl get pods -n credit-card-app -w
```

Wait for `postgres-0` → `1/1 Running`, then `Ctrl+C`.

### 6.2 Auth Service

```bash
kubectl apply -f k8s/auth/
kubectl get pods -n credit-card-app -w
```

Wait for `auth` → `1/1 Running`, then `Ctrl+C`.

**Test it** — open two terminals:

Terminal A (leave running):
```bash
kubectl port-forward deployment/auth 8001:8001 -n credit-card-app
```

Terminal B:
```bash
curl http://localhost:8001/health
```
Expected: `{"status":"ok","service":"auth-service","db":"connected"}`

`Ctrl+C` Terminal A when done.

### 6.3 Application Service

```bash
kubectl apply -f k8s/application/
kubectl get pods -n credit-card-app -w
```

**Test it:**

Terminal A:
```bash
kubectl port-forward deployment/application 8002:8002 -n credit-card-app
```

Terminal B:
```bash
curl http://localhost:8002/health
```

### 6.4 Credit Decision Service

```bash
kubectl apply -f k8s/decision/
kubectl get pods -n credit-card-app -w
```

**Test it:**

Terminal A:
```bash
kubectl port-forward deployment/decision 8003:8003 -n credit-card-app
```

Terminal B:
```bash
curl http://localhost:8003/health
```

### 6.5 Frontend

```bash
kubectl apply -f k8s/frontend/
kubectl get pods -n credit-card-app -w
```

**Test it:**

Terminal A:
```bash
kubectl port-forward deployment/frontend 8090:80 -n credit-card-app
```

Terminal B:
```bash
curl http://localhost:8090/health

curl -X POST http://localhost:8090/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"password123"}'
```
Expected: `201 Created` with a real user JSON object — this proves frontend's Nginx correctly proxies to Auth Service, which correctly connects to `auth_db`.

### 6.6 Ingress — the final piece

```bash
kubectl apply -f k8s/ingress/
kubectl get ingress -n credit-card-app
```

**Full end-to-end test through the real entry point:**

Terminal A:
```bash
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8888:80
```

Terminal B:
```bash
curl http://localhost:8888/health

curl -X POST http://localhost:8888/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User 2","email":"test2@example.com","password":"password123"}'
```

If this returns `201 Created`, the entire chain works: **Ingress → frontend → Auth Service → auth_db**.

---

## 7. Quick health check anytime

```bash
kubectl get pods -n credit-card-app
```

All 5 should show `1/1 Running`:
- `postgres-0`
- `auth-...`
- `application-...`
- `decision-...`
- `frontend-...`

---

## 8. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `CrashLoopBackOff` on `postgres-0` with a "pg_ctlcluster" / mount path error in logs | Image resolved to Postgres 18+. Confirm `k8s/postgres/statefulset.yaml` pins `image: postgres:16-alpine`, not `:latest`. |
| Any backend pod stuck `0/1` with `socket.gaierror` / DNS errors in logs | The service it depends on (usually `postgres`) isn't up yet. Check `kubectl get pods -n credit-card-app` — the pod usually self-heals once its dependency becomes healthy. |
| Frontend crashes on startup with `nginx: [emerg] host not found in upstream` | `nginx.conf`'s `resolver` directive or a `proxy_pass` hostname doesn't match. See section below on frontend DNS. |
| Frontend returns `502 Bad Gateway` on `/api/...` routes, logs show `DNS error (1: Format error)` or `could not be resolved` | Short Kubernetes Service names can fail to resolve reliably from inside Nginx on some clusters. `nginx.conf` in this branch uses fully-qualified names (`auth.credit-card-app.svc.cluster.local`) specifically to avoid this. |
| `kubectl port-forward` fails with "address already in use" | An old port-forward session (in another terminal) is still holding that port. Find and stop it, or use a different local port. |
| First `kubectl apply -f k8s/...` on a brand-new cluster shows a "namespace not found" error for a couple of resources | Expected — resources were applied faster than the namespace fully registered. Simply re-run the same `apply` command once more. |

### Why `nginx.conf` uses fully-qualified Service names

Short names like `http://auth:8001` failed with `DNS error (1: Format error)` / timeouts when queried through Nginx's `resolver` directive on this cluster. The fix was to use Kubernetes' full internal DNS name instead:

```
<service-name>.<namespace>.svc.cluster.local
```

e.g. `auth.credit-card-app.svc.cluster.local:8001` — this is always reliable regardless of resolver/search-domain quirks.

---

## 9. Quick copy-paste: apply a single service folder directly

Useful if you only need to redeploy one service (e.g. after pulling a teammate's update) rather than the whole stack:

```bash
kubectl apply -f ~/credit-card-approval-system/k8s/application/
kubectl get pods -n credit-card-app -w
```

(swap `application` for `postgres`, `auth`, `decision`, `frontend`, or `ingress` as needed — same pattern for each)

---

## 10. Tearing everything down

```bash
kubectl delete namespace credit-card-app
kind delete cluster --name credit-card-app-cluster
```

This removes all app resources and the entire local cluster. Re-run from Step 3 to start fresh.
