# Credit Card Application – EKS Infrastructure

## Overview

The Credit Card application is being migrated from a KIND-based Kubernetes environment to Amazon EKS.

### AWS Environment

| Component | Configuration |
|---|---|
| EKS Cluster | `credit-card-eks` |
| Region | `ap-south-1` |
| Kubernetes | `1.36` |
| VPC CIDR | `10.20.0.0/16` |
| Availability Zones | `ap-south-1a`, `ap-south-1b` |
| Worker Node | `c7i-flex.large` |
| Node OS | Amazon Linux 2023 |
| Node Networking | Private |
| Root Volume | 25 GB gp3 |
| Node Scaling | 0–2 |
| IaC Tool | `eksctl` |

---

## EKS Infrastructure

The EKS cluster is provisioned using `eksctl` and `cluster.yaml`.

`eksctl` uses AWS CloudFormation stacks underneath to create and manage the AWS infrastructure.

### Network

```text
VPC: 10.20.0.0/16

ap-south-1a
├── Public Subnet
└── Private Subnet

ap-south-1b
├── Public Subnet
└── Private Subnet

Private Subnets → NAT Gateway → Internet Gateway

### Managed Node Group

Node Group: app-nodes1
Instance: c7i-flex.large
CPU: 2 vCPU
Memory: 4 GiB
Min: 0
Desired: 1
Max: 2


### EKS Add-Ons

| Add-on                 | Purpose                             |
| ---------------------- | ----------------------------------- |
| VPC CNI                | Pod networking using AWS VPC        |
| CoreDNS                | Kubernetes service/DNS resolution   |
| kube-proxy             | Kubernetes Service networking       |
| EKS Pod Identity Agent | IAM access for Kubernetes workloads |
| AWS EBS CSI Driver     | Persistent EBS storage              |


Current Architecture

                    AWS
                     │
                     ▼
              EKS: credit-card-eks
                     │
              ┌──────┴──────┐
              │             │
          Control Plane   Node Group
                          app-nodes1
                              │
                         c7i-flex.large
                              │
                 ┌────────────┼────────────┐
                 │            │            │
               Pods       PostgreSQL     Services
                              │
                             PVC
                              │
                         gp3 StorageClass
                              │
                         EBS CSI Driver
                              │
                         AWS EBS Volume