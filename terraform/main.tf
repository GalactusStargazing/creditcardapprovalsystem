# ============================================================
# VPC
# ============================================================

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# ============================================================
# Internet Gateway
# ============================================================

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "${var.project_name}-igw"
  }
}


# ============================================================
# Public Subnet
# ============================================================

resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
  cidr_block = var.public_subnet_cidr
  availability_zone = var.availability_zone
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

# ============================================================
# Public Route Table
# ============================================================

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-route-table"
  }
}

# ============================================================
# Associate Public Subnet with Route Table
# ============================================================

resource "aws_route_table_association" "public" {
  subnet_id = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}


# ============================================================
# Security Group
# ============================================================

resource "aws_security_group" "ec2" {

  name = "${var.project_name}-security-group"
  description = "Security group for Kind EC2"
  vpc_id = aws_vpc.main.id


  # ----------------------------------------------------------
  # SSH
  # ----------------------------------------------------------

  ingress {

    description = "SSH"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = [
      var.ssh_allowed_cidr
    ]
  }


  # ----------------------------------------------------------
  # HTTP
  # ----------------------------------------------------------

  ingress {
    description = "HTTP"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  # ----------------------------------------------------------
  # Kubernetes API
  # ----------------------------------------------------------

  ingress {
    description = "Kubernetes API"
    from_port = 6443
    to_port = 6443
    protocol = "tcp"
    cidr_blocks = [
      var.ssh_allowed_cidr
    ]
  }


  # ----------------------------------------------------------
  # Outbound
  # ----------------------------------------------------------

  egress {

    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }


  tags = {
    Name = "${var.project_name}-security-group"
  }
}

# ============================================================
# Generate SSH Private Key
# ============================================================

resource "tls_private_key" "ec2_key" {

  algorithm = "RSA"
  rsa_bits = 4096
}


# ============================================================
# Create AWS Key Pair
# ============================================================

resource "aws_key_pair" "ec2_key" {

  key_name = "${var.project_name}-key"
  public_key = tls_private_key.ec2_key.public_key_openssh
}


# ============================================================
# Save Private Key Locally
# ============================================================

resource "local_sensitive_file" "private_key" {

  filename = "${path.module}/${var.project_name}.pem"
  content = tls_private_key.ec2_key.private_key_pem
  file_permission = "0400"
}


# ============================================================
# EC2 Instance
# ============================================================

resource "aws_instance" "kind" {

  ami = var.ami_id
  instance_type = var.instance_type
  subnet_id = aws_subnet.public.id

  vpc_security_group_ids = [
    aws_security_group.ec2.id
  ]
  key_name = aws_key_pair.ec2_key.key_name
  associate_public_ip_address = true

  # ----------------------------------------------------------
  # Install Docker + kubectl + Kind + Kubernetes
  # ----------------------------------------------------------
  user_data = file(
    "${path.module}/kind-userdata.sh"
  )

  tags = {

    Name = "${var.project_name}-ec2"
  }
}
