output "vpc_id" {
  description = "VPC ID"

  value = aws_vpc.main.id
}


output "public_subnet_id" {
  description = "Public subnet ID"

  value = aws_subnet.public.id
}


output "internet_gateway_id" {
  description = "Internet Gateway ID"

  value = aws_internet_gateway.main.id
}


output "route_table_id" {
  description = "Public route table ID"

  value = aws_route_table.public.id
}


output "security_group_id" {
  description = "Security Group ID"

  value = aws_security_group.ec2.id
}


output "ec2_instance_id" {
  description = "EC2 Instance ID"

  value = aws_instance.kind.id
}


output "ec2_private_ip" {
  description = "EC2 Private IP"

  value = aws_instance.kind.private_ip
}