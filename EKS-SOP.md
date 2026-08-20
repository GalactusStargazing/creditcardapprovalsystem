# SOP — EKS Migration (Credit Card Approval System)

Standard Operating Procedure documenting everything done to migrate the app and monitoring stack from EC2/`kind` to a real AWS EKS cluster, including why specific fixes were needed, full troubleshooting/testing command references, and onboarding steps for teammates.

**Branch:** `eks_deployment` (PR open against `develop`)
**Cluster:** `credit-card-eks`, region `ap-south-1`

---

## 1. Summary of What Was Done Today

| Area | Status |
|---|---|
| EKS node group scaled from 0 → running nodes | ✅ Done |
| EBS CSI driver confirmed installed | ✅ Confirmed |
| App namespace, Secrets, all 5 workloads deployed | ✅ Done |
| Ingress Controller (AWS-specific nginx build) installed | ✅ Done |
| Real AWS Load Balancer provisioned and working | ✅ Confirmed |
| Frontend → backend internal DNS bug fixed | ✅ Fixed & tested |
| `gp3` storage class made cluster default | ✅ Fixed & tested |
| Full app flow tested (register/login/apply/decision) | ✅ Confirmed working |
| Monitoring stack (Prometheus/Grafana/AlertManager/Loki) installed on EKS | ✅ Done |
| Grafana persistent storage bug found and fixed | ✅ Fixed & tested |
| Data durability proven with a real pod-restart test | ✅ Confirmed |
| Discord alerting tested end-to-end on EKS | ✅ Confirmed |
| `decision-service` DB password exposure (ConfigMap→Secret) | ✅ Fixed (separate PR, already merged) |
| AWS key accidentally hardcoded in a workflow file | 🚨 Caught by GitHub push protection, reported to admin for rotation |
| CI/CD SSH→EKS conversion (`application-cicd.yml`) | ⏳ Drafted, not committed — needs `workflow` token scope or teammate to finish |

---

## 2. Phase A — One-Time Cluster Bootstrap

### 2.1 Switch context and confirm cluster health

```bash
kubectl config get-contexts
kubectl config use-context <eks-context-name>
kubectl get nodes
```
**Why:** confirms `kubectl` is genuinely talking to EKS, not a leftover local `kind` context — this exact mix-up has caused real confusion earlier in this project.

### 2.2 Check/scale the node group (if nodes are missing)

```bash
aws eks describe-nodegroup --cluster-name credit-card-eks --nodegroup-name <name> --region ap-south-1 \
  --query "nodegroup.{Status:status,Health:health,Desired:scalingConfig.desiredSize}"
```
**Root cause found today:** node group existed and was `ACTIVE`, but `desiredSize: 0` — meaning zero EC2 instances were ever launched. Fixed via:
```bash
aws eks update-nodegroup-config \
  --cluster-name credit-card-eks --nodegroup-name <name> \
  --scaling-config minSize=1,maxSize=3,desiredSize=2 \
  --region ap-south-1
```

### 2.3 Confirm the EBS CSI driver is installed

```bash
kubectl get pods -n kube-system | grep ebs-csi
```
**Why this matters:** without this driver, no PersistentVolumeClaim can ever actually bind to real storage — Postgres and Grafana would both stay stuck `Pending` forever.

### 2.4 Create the app namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2.5 Create the storage class

```bash
kubectl apply -f k8s/postgres/gp3-storageclass.yaml
```
**Why `gp3` specifically, and why we edited this file today:**
- The cluster's pre-existing `gp2` storage class uses the **older, in-tree** `kubernetes.io/aws-ebs` provisioner.
- `gp3` uses the **modern** `ebs.csi.aws.com` provisioner (the one the EBS CSI driver actually implements), is generally cheaper and faster than `gp2`, and supports `allowVolumeExpansion: true`.
- **The real bug found today:** neither `gp2` nor `gp3` was marked as the cluster's *default* storage class. Any PVC that doesn't explicitly name a `storageClassName` (Grafana's, by default) had nothing to fall back to, and failed with `persistentvolumeclaim ... not found`.
- **Fix:** added this annotation to `gp3-storageclass.yaml`:
  ```yaml
  metadata:
    name: gp3
    annotations:
      storageclass.kubernetes.io/is-default-class: "true"
  ```

### 2.6 Recreate every real Secret, fresh, on this cluster

Secrets never travel via git — recreate them directly on each new cluster:
```bash
cd k8s/postgres && cp secret.yaml.example secret.yaml && nano secret.yaml && kubectl apply -f secret.yaml
cd ../auth && cp secret.yaml.example secret.yaml && nano secret.yaml && kubectl apply -f secret.yaml
cd ../application && cp secret.yaml.example secret.yaml && nano secret.yaml && kubectl apply -f secret.yaml
cd ../decision && cp secret.yaml.example secret.yaml && nano secret.yaml && kubectl apply -f secret.yaml
```
**Rule that must hold:** identical Postgres password across all four; identical `JWT_SECRET_KEY` between `auth` and `application` specifically.

### 2.7 Deploy Postgres, wait for healthy, then the rest

```bash
kubectl apply -f k8s/postgres/
kubectl get pods -n credit-card-app -w   # wait for postgres-0 to be 1/1 Running
kubectl apply -f k8s/auth/
kubectl apply -f k8s/application/
kubectl apply -f k8s/decision/
kubectl apply -f k8s/frontend/
```

### 2.8 Fix the frontend's internal DNS resolver — REQUIRED, cluster-specific

**The bug:** `frontend/nginx.conf` had a hardcoded CoreDNS resolver IP from the *old* EC2/`kind` cluster:
```nginx
resolver 10.96.0.10 valid=10s;
```
On EKS, CoreDNS (named `kube-dns` here) has a **different** ClusterIP. Find it with:
```bash
kubectl get svc -n kube-system | grep dns
```
Update `nginx.conf` to the real value (found today: `172.20.0.10`), then rebuild and redeploy:
```bash
cd frontend
docker build --no-cache -t ccs-frontend:latest .
docker tag ccs-frontend:latest pranjal261/credit-card-frontend:latest
docker push pranjal261/credit-card-frontend:latest
kubectl rollout restart deployment frontend -n credit-card-app
```
**Symptom this fixes:** `502 Bad Gateway` on `/api/v1/auth/register` and `/login`, with frontend logs showing `could not be resolved (110: Operation timed out)`.
**Important for future clusters:** this resolver IP will very likely be different again on any new cluster — check it fresh every time, don't assume.

### 2.9 Install the Ingress Controller (AWS-specific build)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/aws/deploy.yaml
kubectl get pods -n ingress-nginx -w
```
**Why the AWS-specific URL, not the `kind` one used previously:** this version provisions a Service of `type: LoadBalancer`, which tells AWS to create a real, public Elastic Load Balancer automatically. The `kind` version has no concept of this at all.

### 2.10 Apply the app's Ingress rules

```bash
kubectl apply -f k8s/ingress/ingress.yaml
```

### 2.11 Get the load balancer's address

```bash
kubectl get svc ingress-nginx-controller -n ingress-nginx -w
```
Wait for `EXTERNAL-IP` to populate — it will be a **DNS hostname**, not a plain IP (e.g., `xxxxx.ap-south-1.elb.amazonaws.com`).

---

## 3. Phase B — Monitoring Installation

### 3.1 Namespace and Helm repo

```bash
cd monitoring
kubectl apply -f namespace.yaml
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### 3.2 Secrets

```bash
cp grafana-admin-secret.yaml.example grafana-admin-secret.yaml
nano grafana-admin-secret.yaml && kubectl apply -f grafana-admin-secret.yaml

cp discord-webhook-secret.yaml.example discord-webhook-secret.yaml
nano discord-webhook-secret.yaml && kubectl apply -f discord-webhook-secret.yaml
```

### 3.3 Discord relay and the main stack

```bash
kubectl apply -f alertmanager-discord.yaml
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --values values.yaml
```

### 3.4 The Grafana storage bug found today — separate from the `gp3` default fix

Even after making `gp3` the cluster default, Grafana's pod was **still** stuck `Pending` after a manual PVC delete/recreate test, with error `persistentvolumeclaim "monitoring-grafana" not found`.

**Root cause:** Grafana is a plain **Deployment**, not a StatefulSet — unlike Postgres, it has no `volumeClaimTemplates` mechanism to auto-recreate a deleted PVC. Once deleted, nothing rebuilds it except a fresh `helm install`/`helm upgrade`.

**Fix — made the dependency explicit in `values.yaml`, rather than relying on the cluster default silently working:**
```yaml
grafana:
  persistence:
    enabled: true
    size: 100Mi
    storageClassName: gp3
```
```bash
helm upgrade monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --values values.yaml
```

### 3.5 Alert rule and Ingress

```bash
kubectl apply -f pod-down-alert.yaml
kubectl apply -f ingress.yaml
```

### 3.6 ServiceMonitors (from the app's own folders)

```bash
kubectl apply -f ../k8s/auth/servicemonitor.yaml
kubectl apply -f ../k8s/application/servicemonitor.yaml
kubectl apply -f ../k8s/decision/servicemonitor.yaml
```

---

## 4. Troubleshooting Commands Reference

| Symptom | Command | What it tells you |
|---|---|---|
| Pod stuck `Pending` | `kubectl describe pod <name> -n <ns>` | Check the `Events:` section at the bottom — usually names the exact blocker |
| PVC stuck `Pending` | `kubectl get pvc -n <ns>` then `kubectl describe pvc <name> -n <ns>` | Confirms storage class mismatch or missing CSI driver |
| Node group shows no nodes | `aws eks describe-nodegroup --cluster-name credit-card-eks --nodegroup-name <name> --region ap-south-1 --query "nodegroup.{Status:status,Health:health,Desired:scalingConfig.desiredSize}"` | Checks `desiredSize` — the exact bug found today |
| 502 Bad Gateway from frontend | `kubectl logs -n credit-card-app -l app=frontend --tail=50` | Shows the real Nginx error, e.g. DNS resolution failure |
| Service missing from Prometheus targets | `kubectl get svc <name> -n credit-card-app --show-labels` | Confirms `metadata.labels` matches the ServiceMonitor's `matchLabels` |
| ServiceMonitor exists but target shows `UNKNOWN`, never scraped | Wait 1-2 minutes, refresh; if still stuck, `kubectl delete pod -l app=<service> -n credit-card-app` | Usually just a first-scrape-cycle timing issue |
| AlertManager not sending to Discord | `kubectl get alertmanager -n monitoring` — check `RECONCILED` column | `False` means the config failed to load; `kubectl describe alertmanager <name> -n monitoring` shows the exact error |
| Discord relay not receiving alerts | `kubectl logs -n monitoring -l app=alertmanager-discord --tail=30` | Confirms whether POST requests are actually arriving |
| `kubectl get nodes` returns nothing | `kubectl config current-context` | Confirms you're not accidentally still pointed at a local `kind` cluster |

---

## 5. Testing / Validation Commands

### 5.1 App end-to-end
```bash
curl -s http://<elb-hostname>/ | head -5
```
Then manually: register → login → submit an application → confirm a decision returns.

### 5.2 Storage durability — genuine proof, not just "looks Bound"
```bash
kubectl exec -it postgres-0 -n credit-card-app -- psql -U ccapp -d application_db -c "SELECT COUNT(*) FROM applications;"
kubectl get pvc -n credit-card-app   # note the VOLUME name
kubectl delete pod postgres-0 -n credit-card-app
kubectl get pods -n credit-card-app -w   # wait for 1/1 Running
kubectl get pvc -n credit-card-app   # confirm SAME volume name
kubectl exec -it postgres-0 -n credit-card-app -- psql -U ccapp -d application_db -c "SELECT COUNT(*) FROM applications;"
# count must match exactly
```

### 5.3 Monitoring targets
```
http://<elb-hostname>/prometheus/targets
```
Confirm `auth`, `application`, `decision` all show `UP` (click "Show empty pools" if hidden).

### 5.4 Discord alert fire/resolve test
```bash
kubectl scale deployment decision -n credit-card-app --replicas=0
# wait a genuine 3 minutes, do not check early
kubectl scale deployment decision -n credit-card-app --replicas=1
```
Confirm a `[FIRING]` message, then a `[RESOLVED]` message, both in Discord.

---

## 6. Log Scanning Commands

```bash
# Any pod's current logs
kubectl logs <pod-name> -n <namespace>

# Logs from before the last crash
kubectl logs <pod-name> -n <namespace> --previous

# All pods matching a label, tail only
kubectl logs -l app=<service> -n credit-card-app --tail=50

# Search via Loki, in Grafana's Explore view, once Loki is installed
{namespace="credit-card-app", app="auth"} |= "ERROR"
{namespace="credit-card-app"} != "/health"    # filters out constant health-check noise
```

---

## 7. What a Teammate Needs To Do After This PR Is Merged

### 7.1 Can they just access the URLs directly? — Yes, genuinely, with one honest caveat

Unlike the old EC2 setup (which needed an Elastic IP and manual instance start/stop), **EKS nodes stay running continuously as long as the node group's `desiredSize` stays above 0** — there's no "start the instance" step for a teammate to do. The app and monitoring URLs work **right now, for anyone**, no `kubectl` or AWS access required:

```
App:        http://a86c4cf2dbb344884a657cef8d8f4316-83262784c03742fc.elb.ap-south-1.amazonaws.com
Grafana:    http://a86c4cf2dbb344884a657cef8d8f4316-83262784c03742fc.elb.ap-south-1.amazonaws.com/grafana
Prometheus: http://a86c4cf2dbb344884a657cef8d8f4316-83262784c03742fc.elb.ap-south-1.amazonaws.com/prometheus
```

**The honest caveat:** this exact hostname isn't permanently guaranteed — if the Ingress Controller's Service is ever deleted and recreated, AWS may assign a *different* load balancer hostname. Worth pointing a real, registered domain at this via a DNS record eventually, so this URL never needs to be re-shared.

### 7.2 If a teammate wants to actually run `kubectl`/`helm` commands against this cluster themselves

1. Get AWS credentials with EKS access from an admin
2. `aws configure` with those credentials
3. `aws eks update-kubeconfig --name credit-card-eks --region ap-south-1`
4. `kubectl get nodes` to confirm access

### 7.3 If a teammate wants to redeploy after pulling this branch

Nothing needs redeploying just from pulling code — the cluster is already running the current state. Redeployment is only needed if they make a **new** code change:
```bash
docker build --no-cache -t ccs-<service>:latest ./<service>-service
docker tag ccs-<service>:latest pranjal261/credit-card-<service>-service:latest
docker push pranjal261/credit-card-<service>-service:latest
kubectl set image deployment/<service> <service>=pranjal261/credit-card-<service>-service:latest -n credit-card-app
kubectl rollout status deployment/<service> -n credit-card-app
```

### 7.4 Genuinely important, standing reminder for the whole team

**Never type a real AWS Access Key or Secret Key directly into a workflow file, script, or any committed file — always reference `${{ secrets.X }}`.** A real key was caught today by GitHub's push protection before it reached the repo; it still had to be treated as compromised and rotated. Always double-check `git diff` for anything resembling a real credential before committing, especially in `.github/workflows/` files.
