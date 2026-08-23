#!/bin/bash

set -euxo pipefail


# ============================================================
# Logging
# ============================================================

exec > >(tee /var/log/kind-install.log | logger -t kind-userdata -s 2>/dev/console) 2>&1


echo "=========================================="
echo "Starting Kind installation"
echo "=========================================="


# ============================================================
# Update Ubuntu
# ============================================================

apt-get update -y


# ============================================================
# Install required packages
# ============================================================

apt-get install -y \
    docker.io \
    curl \
    ca-certificates


# ============================================================
# Start Docker
# ============================================================

systemctl enable docker

systemctl start docker


# ============================================================
# Add ubuntu user to Docker group
# ============================================================

usermod -aG docker ubuntu


# ============================================================
# Install kubectl
# ============================================================

KUBECTL_VERSION="v1.30.0"

curl -LO \
    "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"

install \
    -o root \
    -g root \
    -m 0755 \
    kubectl \
    /usr/local/bin/kubectl

rm -f kubectl


# ============================================================
# Install Kind
# ============================================================

KIND_VERSION="v0.29.0"

curl -Lo \
    /tmp/kind \
    "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-amd64"

chmod +x /tmp/kind

mv /tmp/kind /usr/local/bin/kind


# ============================================================
# Verify installations
# ============================================================

echo "Docker:"
docker --version

echo "kubectl:"
kubectl version --client

echo "Kind:"
kind version


# ============================================================
# Create Kind configuration
# ============================================================

cat > /home/ubuntu/kind-config.yaml <<'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4

nodes:
  - role: control-plane
  - role: worker
  - role: worker
EOF


chown ubuntu:ubuntu /home/ubuntu/kind-config.yaml


# ============================================================
# Create .kube directory
# ============================================================

mkdir -p /home/ubuntu/.kube

chown -R ubuntu:ubuntu /home/ubuntu/.kube


# ============================================================
# Create Kind Kubernetes cluster
# ============================================================

echo "=========================================="
echo "Creating Kind cluster"
echo "=========================================="


sudo -u ubuntu -H kind create cluster \
    --name dev-cluster \
    --config /home/ubuntu/kind-config.yaml


# ============================================================
# Export kubeconfig
# ============================================================

echo "=========================================="
echo "Exporting kubeconfig"
echo "=========================================="


sudo -u ubuntu -H kind export kubeconfig \
    --name dev-cluster \
    --kubeconfig /home/ubuntu/.kube/config


chown ubuntu:ubuntu /home/ubuntu/.kube/config

chmod 600 /home/ubuntu/.kube/config


# ============================================================
# Verify Kind nodes
# ============================================================

echo "=========================================="
echo "Kind nodes"
echo "=========================================="


sudo -u ubuntu -H kind get nodes \
    --name dev-cluster


# ============================================================
# Verify Kubernetes nodes
# ============================================================

echo "=========================================="
echo "Kubernetes nodes"
echo "=========================================="


sudo -u ubuntu -H kubectl \
    --kubeconfig /home/ubuntu/.kube/config \
    get nodes -o wide


# ============================================================
# Verify Kubernetes pods
# ============================================================

echo "=========================================="
echo "Kubernetes system pods"
echo "=========================================="


sudo -u ubuntu -H kubectl \
    --kubeconfig /home/ubuntu/.kube/config \
    get pods -A


echo "=========================================="
echo "Kind cluster installation completed"
echo "=========================================="