variable "aws_region" {
  description = "AWS region"
  type        = string
}


variable "project_name" {
  description = "Project name"
  type        = string
}


variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}


variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
}


variable "availability_zone" {
  description = "Availability zone"
  type        = string
}


variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}


variable "ssh_allowed_cidr" {
  description = "CIDR allowed to SSH into EC2"
  type        = string
}


variable "ami_id" {
  description = "AMI ID for EC2 instance"
  type        = string
}
