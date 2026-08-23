# AWS EC2 + Kind Kubernetes Cluster using Terraform

## Overview

This project provisions a complete AWS environment using Terraform and then uses an Ubuntu EC2 instance to run a local Kubernetes cluster using **Kind (Kubernetes IN Docker)**.

The project is designed as a hands-on DevOps/Kubernetes lab.

Terraform is responsible for creating the AWS infrastructure, while EC2 User Data automatically installs Docker, kubectl, and Kind and creates a multi-node Kubernetes cluster.

### What this project creates

* AWS VPC
* Public subnet
* Internet Gateway
* Public route table
* Route table association
* Security Group
* SSH key pair
* Ubuntu EC2 instance
* Docker
* kubectl
* Kind
* Kubernetes control-plane node
* Two Kubernetes worker nodes

---

# Architecture

```text
                              Internet
                                  |
                                  |
                         +--------v---------+
                         | Internet Gateway |
                         +--------+---------+
                                  |
                                  |
                         +--------v---------+
                         |       VPC        |
                         |   10.0.0.0/16    |
                         |                  |
                         |  Public Subnet   |
                         |   10.0.1.0/24    |
                         |                  |
                         |  +------------+  |
                         |  | Ubuntu EC2 |  |
                         |  |            |  |
                         |  |   Docker   |  |
                         |  |     |      |  |
                         |  |    Kind    |  |
                         |  |     |      |  |
                         |  |  +---------+|  |
                         |  |  |Control  ||  |
                         |  |  |Plane    ||  |
                         |  |  +---------+|  |
                         |  |  +---------+|  |
                         |  |  | Worker  ||  |
                         |  |  +---------+|  |
                         |  |  +---------+|  |
                         |  |  | Worker  ||  |
                         |  |  +---------+|  |
                         |  +------------+  |
                         +------------------+
```

---

# Architecture Flow

The infrastructure is created in the following order:

```text
Terraform
   |
   v
VPC
   |
   +---- Internet Gateway
   |
   +---- Public Subnet
   |
   +---- Route Table
   |
   +---- Security Group
   |
   +---- SSH Key Pair
   |
   v
Ubuntu EC2
   |
   +---- Docker
   |
   +---- kubectl
   |
   +---- Kind
           |
           +---- Control Plane
           |
           +---- Worker 1
           |
           +---- Worker 2
```

---

# Project Structure

The project is organized approximately as follows:

```text
Terra_Project/
|
+-- main.tf
+-- variables.tf
+-- output.tf
+-- terraform.tfvars
+-- kind-userdata.sh
+-- .gitignore
+-- README.md
```

## File Responsibilities

### `main.tf`

Contains the main AWS infrastructure resources.

It is responsible for:

* AWS provider configuration
* VPC
* Internet Gateway
* Public subnet
* Route table
* Route table association
* Security Group
* EC2 key pair
* EC2 instance

The EC2 instance also references the Kind user-data script.

---

### `variables.tf`

Contains configurable Terraform variables such as:

* AWS region
* Project name
* VPC CIDR
* Public subnet CIDR
* Availability Zone
* AMI ID
* EC2 instance type
* Public IP allowed for SSH

Keeping these values in variables makes the infrastructure reusable.

---

### `terraform.tfvars`

Contains environment-specific values.

For example:

```text
AWS region
VPC CIDR
Subnet CIDR
Availability Zone
Ubuntu AMI
EC2 instance type
Your public IP
```

This file allows you to change environment settings without modifying the Terraform resource definitions.

---

### `output.tf`

Contains Terraform outputs such as:

* VPC ID
* Public subnet ID
* Internet Gateway ID
* Route table ID
* Security Group ID
* EC2 instance ID
* EC2 private IP
* EC2 public IP
* Key pair name

The EC2 public IP is particularly useful for SSH access.

---

### `kind-userdata.sh`

This script runs automatically when the Ubuntu EC2 instance starts for the first time.

It installs:

1. Docker
2. kubectl
3. Kind

It then:

1. Starts Docker
2. Adds the Ubuntu user to the Docker group
3. Creates a Kind configuration
4. Creates a Kubernetes cluster
5. Creates one control-plane node
6. Creates two worker nodes
7. Configures kubeconfig
8. Verifies the Kubernetes nodes

---

# AWS Networking

## VPC

The project creates a VPC using a private CIDR range.

Example:

```text
10.0.0.0/16
```

This provides the overall IP address space for the AWS environment.

The VPC is the logical network boundary for the EC2 instance.

---

# Public Subnet

A public subnet is created inside the VPC.

Example:

```text
10.0.1.0/24
```

The EC2 instance is launched inside this subnet.

The subnet is considered public because its route table contains a default route to the Internet Gateway.

---

# Internet Gateway

The Internet Gateway provides connectivity between the VPC and the internet.

Traffic flow:

```text
EC2
 |
 v
Public Subnet
 |
 v
Route Table
 |
 | 0.0.0.0/0
 v
Internet Gateway
 |
 v
Internet
```

The Internet Gateway is attached to the VPC.

---

# Route Table

The public route table contains a default route:

```text
Destination: 0.0.0.0/0
Target: Internet Gateway
```

This means traffic destined for addresses outside the VPC is sent through the Internet Gateway.

The public subnet is associated with this route table.

---

# Security Group

A Security Group is attached to the EC2 instance.

It controls inbound and outbound traffic.

Typical inbound rules for this lab are:

```text
SSH
Port: 22
Protocol: TCP
Source: Your public IP /32
```

HTTP and HTTPS can be opened if required for Kubernetes applications:

```text
HTTP
Port: 80
Protocol: TCP

HTTPS
Port: 443
Protocol: TCP
```

Outbound traffic is allowed as required by the lab.

---

# Security Considerations

SSH should preferably be restricted to your own public IP.

For example:

```text
YOUR_PUBLIC_IP/32
```

Avoid exposing SSH to:

```text
0.0.0.0/0
```

unless you are intentionally creating a temporary disposable lab.

The `/32` notation means only one IP address is allowed.

---

# SSH Key Pair

The project uses Terraform to generate an SSH key pair.

The process is:

```text
Terraform
    |
    v
Generate private/public key
    |
    +---- Public Key ---> AWS EC2 Key Pair
    |
    +---- Private Key --> Local .pem file
```

The public key is registered with AWS.

The private key remains on the local machine and is used to connect to the EC2 instance.

The private key should never be committed to Git.

---

# Ubuntu EC2

The EC2 instance uses an Ubuntu AMI.

The default SSH username for Ubuntu is:

```text
ubuntu
```

After Terraform creates the EC2 instance, connect using:

```text
ssh -i <private-key> ubuntu@<public-ip>
```

The private key must have restrictive permissions.

Typical permission:

```text
400
```

---

# EC2 User Data

The EC2 User Data script automates the Kubernetes environment setup.

The process is:

```text
EC2 Boot
   |
   v
Update Ubuntu
   |
   v
Install Docker
   |
   v
Start Docker
   |
   v
Install kubectl
   |
   v
Install Kind
   |
   v
Create Kind configuration
   |
   v
Create Kubernetes cluster
   |
   v
Configure kubeconfig
   |
   v
Verify nodes
```

This means Kubernetes does not need to be installed manually after logging into the EC2.

---

# Docker

Kind requires Docker as the container runtime.

The EC2 installs Docker and starts the Docker service.

Docker runs the Kubernetes nodes as containers.

The architecture is therefore:

```text
Ubuntu EC2
    |
    v
Docker
    |
    +---- Control Plane Container
    |
    +---- Worker Container
    |
    +---- Worker Container
```

---

# Kind

Kind stands for:

```text
Kubernetes IN Docker
```

Kind is primarily designed for running Kubernetes clusters for development, testing, and learning.

In this project, the Kubernetes nodes are Docker containers running inside the EC2 instance.

Kind does not create traditional EC2-based Kubernetes worker nodes.

Instead:

```text
EC2
 |
 +-- Docker
      |
      +-- Kubernetes Control Plane Container
      |
      +-- Kubernetes Worker Container
      |
      +-- Kubernetes Worker Container
```

---

# Kubernetes Cluster

The project creates a three-node Kind cluster:

```text
dev-cluster
|
+-- Control Plane
|
+-- Worker 1
|
+-- Worker 2
```

The control-plane node manages the Kubernetes cluster.

The worker nodes run application workloads.

---

# Kubernetes Control Plane

The control-plane node contains Kubernetes control-plane components such as:

* API Server
* Scheduler
* Controller Manager
* etcd

The control plane is responsible for maintaining the desired state of the cluster.

---

# Kubernetes Worker Nodes

The worker nodes are responsible for running application workloads.

They contain components such as:

* kubelet
* kube-proxy
* container runtime

In Kind, these nodes are represented by Docker containers.

---

# Verify Kubernetes

After connecting to the EC2:

Check Kind:

```text
kind version
```

Check the Kind clusters:

```text
kind get clusters
```

Expected:

```text
dev-cluster
```

Check Kubernetes nodes:

```text
kubectl get nodes
```

Expected output:

```text
NAME                        STATUS   ROLES           AGE
dev-cluster-control-plane   Ready    control-plane   ...
dev-cluster-worker          Ready   <none>          ...
dev-cluster-worker2         Ready   <none>          ...
```

---

# Verify Docker

Check Docker:

```text
docker --version
```

Check running containers:

```text
docker ps
```

You should see containers corresponding to the Kind Kubernetes nodes.

---

# Useful Kubernetes Commands

Get nodes:

```text
kubectl get nodes
```

Get pods in all namespaces:

```text
kubectl get pods -A
```

Get namespaces:

```text
kubectl get namespaces
```

Get services:

```text
kubectl get svc -A
```

Get deployments:

```text
kubectl get deployments -A
```

Describe a node:

```text
kubectl describe node <node-name>
```

Get cluster information:

```text
kubectl cluster-info
```

---

# Terraform Workflow

The typical workflow is:

```text
terraform init
        |
        v
terraform fmt
        |
        v
terraform validate
        |
        v
terraform plan
        |
        v
terraform apply
```

---

# Terraform Initialization

Initialize the Terraform project:

```text
terraform init
```

This downloads the required Terraform providers and prepares the working directory.

---

# Terraform Formatting

Format Terraform files:

```text
terraform fmt
```

This keeps Terraform configuration consistently formatted.

---

# Terraform Validation

Validate the configuration:

```text
terraform validate
```

A successful validation means Terraform configuration syntax and basic configuration structure are valid.

---

# Terraform Plan

Before creating infrastructure:

```text
terraform plan
```

This shows what Terraform intends to create, modify, or destroy.

Always review the plan before applying changes.

---

# Terraform Apply

Create the infrastructure:

```text
terraform apply
```

Terraform will create the AWS infrastructure and launch the EC2 instance.

During EC2 startup, the User Data script installs Docker, kubectl, Kind, and creates the Kubernetes cluster.

---

# Connecting to the EC2

After Terraform finishes, obtain the EC2 public IP from the Terraform outputs.

Then connect using SSH:

```text
ssh -i <private-key> ubuntu@<public-ip>
```

Once connected:

```text
ubuntu@ip-10-0-1-xxx:~$
```

---

# Complete Deployment Flow

The complete deployment process is:

```text
Developer
    |
    | terraform apply
    v
Terraform
    |
    +----------------------------+
    |                            |
    v                            v
AWS Networking              EC2 Instance
    |                            |
    |                            v
    |                         User Data
    |                            |
    |                    +-------+-------+
    |                    |       |       |
    |                  Docker kubectl  Kind
    |                            |
    |                            v
    |                     Kubernetes
    |                            |
    |                +-----------+-----------+
    |                |           |           |
    |                v           v           v
    |             Control     Worker      Worker
    |              Plane        1           2
    |
    v
Internet connectivity
```

---

# Troubleshooting

## Only Control Plane Is Showing

If:

```text
kubectl get nodes
```

shows only:

```text
dev-cluster-control-plane
```

the cluster was probably created using the default Kind command without a multi-node configuration.

A default Kind cluster creates a single control-plane node.

The desired configuration is:

```text
Control Plane
+
Worker 1
+
Worker 2
```

The Kind configuration must explicitly define the worker nodes.

---

# User Data Changes Are Not Applied Automatically

A common Terraform surprise is changing the User Data script and expecting the existing EC2 instance to execute it again.

EC2 User Data normally runs during the initial instance boot.

If the EC2 already exists, changing the script does not mean the existing instance will automatically rerun the entire script.

For a lab environment, recreate/replace the EC2 instance after modifying User Data.

For example, Terraform can be instructed to replace the instance.

Be careful because replacing the instance destroys the existing EC2 and creates a new one.

---

# Terraform Duplicate Resource Error

If Terraform reports:

```text
Duplicate resource "aws_instance" configuration
```

check that the same resource has not been defined twice.

For example, this cannot exist twice in the same Terraform module:

```text
aws_instance.web
```

Terraform treats all `.tf` files in the same directory as one module.

Therefore:

```text
main.tf
kind.tf
```

do not create separate Terraform namespaces.

The resource name must be unique across the entire directory/module.

---

# Terraform Undeclared Resource Error

If Terraform reports:

```text
Reference to undeclared resource
```

for something such as:

```text
aws_instance.web
```

it means the resource is being referenced but Terraform cannot find its declaration.

For example, an output may reference the EC2 instance while the EC2 resource itself has been removed.

Make sure the EC2 resource exists exactly once.

---

# SSH Connection Timeout

If SSH times out, check:

1. EC2 has a public IP.
2. EC2 is in the public subnet.
3. Public subnet has a route to the Internet Gateway.
4. Security Group allows TCP port 22.
5. Security Group source allows your current public IP.
6. Network ACLs are not blocking traffic.
7. The EC2 instance is running.

The expected network path is:

```text
Mac
 |
 v
Internet
 |
 v
Internet Gateway
 |
 v
Public Subnet
 |
 v
Security Group
 |
 v
EC2 :22
```

---

# SSH Permission Denied

If you receive:

```text
Permission denied (publickey)
```

check:

* Correct private key
* Correct EC2 username
* Correct AWS key pair
* Private key permissions
* Public key registered with the EC2 instance

For Ubuntu, the SSH username is normally:

```text
ubuntu
```

not:

```text
ec2-user
```

---

# Docker Permission Denied

If you receive an error indicating that the Ubuntu user cannot access Docker, check:

```text
groups
```

The user should belong to the Docker group.

Because group membership is established during setup, a new SSH session may be required before the group membership is reflected.

---

# Check User Data Logs

If Kind was not installed successfully, check the EC2 User Data logs.

The main cloud-init output can be inspected using:

```text
sudo cat /var/log/cloud-init-output.log
```

Also check:

```text
sudo cat /var/log/cloud-init.log
```

These logs are extremely useful when Terraform successfully creates the EC2 but the Kubernetes setup fails.

---

# Check Kind

Run:

```text
kind get clusters
```

If the cluster exists:

```text
kind get nodes
```

Then:

```text
kubectl get nodes
```

---

# Check Docker Containers

Kind nodes are Docker containers.

Run:

```text
docker ps
```

You should see containers representing:

```text
control-plane
worker
worker
```

This is one of the easiest ways to understand how Kind works internally.

---

# Important Limitations

This project is intended primarily for:

* Learning
* Kubernetes practice
* DevOps experimentation
* CI/CD testing
* Helm practice
* GitOps practice
* Argo CD experiments
* Kubernetes troubleshooting
* Local cluster development

It is **not intended to be a production Kubernetes architecture**.

Kind running inside a single EC2 instance creates a single underlying infrastructure failure domain.

If the EC2 instance fails, the entire Kind cluster disappears.

---

# Production Comparison

This lab:

```text
AWS
 |
 EC2
 |
 Docker
 |
 Kind
 |
 Kubernetes
```

A production AWS Kubernetes architecture would generally use:

```text
AWS
 |
 VPC
 |
 EKS
 |
 +-- Managed Control Plane
 |
 +-- Worker Nodes / Managed Node Groups
 |
 +-- Load Balancers
 |
 +-- IAM
 |
 +-- VPC Networking
 |
 +-- CloudWatch / Prometheus / Grafana
```

Kind is therefore excellent for learning Kubernetes mechanics, while EKS is designed for production-grade AWS Kubernetes workloads.

---

# Cleanup

When you are finished with the lab, destroy the AWS resources:

```text
terraform destroy
```

Review the resources Terraform plans to delete and confirm the operation.

This is important because EC2, networking, and other AWS resources can incur charges.

---

# Security Checklist

Before using this project beyond a temporary lab:

* Restrict SSH to your IP.
* Never commit private keys.
* Never commit Terraform state containing sensitive information.
* Protect Terraform state.
* Use encrypted remote state for team environments.
* Avoid exposing Kubernetes API ports directly to the internet.
* Avoid using `0.0.0.0/0` for SSH.
* Use IAM with least privilege.
* Use Systems Manager Session Manager where appropriate.
* Rotate credentials when necessary.

---

# Learning Objectives

After completing this project, you should understand the relationship between:

```text
Terraform
   |
   +-- AWS VPC
   +-- Subnet
   +-- Internet Gateway
   +-- Route Table
   +-- Security Group
   +-- Key Pair
   +-- EC2
        |
        +-- Ubuntu
             |
             +-- Docker
                  |
                  +-- Kind
                       |
                       +-- Kubernetes
                            |
                            +-- Control Plane
                            +-- Worker Nodes
```

This project is particularly useful for understanding the difference between **AWS infrastructure provisioning** and **Kubernetes cluster provisioning**.

Terraform creates the AWS infrastructure.

The EC2 User Data script bootstraps the software environment.

Kind creates the Kubernetes cluster.

kubectl communicates with that Kubernetes cluster.

---

# Final Result

At the end of the deployment, you should have:

```text
AWS VPC
|
+-- Public Subnet
|      |
|      +-- Ubuntu EC2
|             |
|             +-- Docker
|             |
|             +-- kubectl
|             |
|             +-- Kind
|                    |
|                    +-- Control Plane
|                    |
|                    +-- Worker 1
|                    |
|                    +-- Worker 2
|
+-- Internet Gateway
|
+-- Route Table
|
+-- Security Group
|
+-- SSH Key Pair
```

The final Kubernetes check should show three nodes:

```text
kubectl get nodes

NAME                        STATUS   ROLES
dev-cluster-control-plane   Ready    control-plane
dev-cluster-worker          Ready    <none>
dev-cluster-worker2         Ready    <none>
```

This gives you a compact AWS-based Kubernetes playground that can later be extended with **Helm, Ingress, Argo CD, Prometheus, Grafana, Istio, GitLab/Jenkins CI/CD, and GitOps workflows**.
