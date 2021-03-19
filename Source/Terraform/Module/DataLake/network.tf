resource "aws_vpc" "datalake" {
    cidr_block              = "172.31.0.0/16"
    enable_dns_hostnames    = true

    tags = merge(local.tags, {Name = "Data Lake VPC"})
}


resource "aws_internet_gateway" "datalake" {
    vpc_id = aws_vpc.datalake.id

    tags = merge(local.tags, {Name = "Data Lake Internet Gateway"})
}


resource "aws_route" "datalake" {
    route_table_id              = aws_vpc.datalake.default_route_table_id
    destination_cidr_block      = "0.0.0.0/0"
    gateway_id                  = aws_internet_gateway.datalake.id
}


resource "aws_security_group" "datalake" {
  name        = "Data Lake"
  description = "Allow all inbound traffic from bastions and the same security group"
  vpc_id      = aws_vpc.datalake.id

    ingress {
        description = "All"
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        self        = true
        security_groups = [aws_security_group.bastion_ssh.id]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = merge(local.tags, {Name = "Data Lake"})
}

# resource "aws_vpc_endpoint" "datalake" {
#     vpc_id          = aws_vpc.datalake.id
#     service_name    = "com.amazonaws.us-east-1.execute-api"
#     vpc_endpoint_type = "Interface"
#     private_dns_enabled = false
#
#     security_group_ids = [
#         aws_security_group.datalake.id
#     ]
#
#     tags = merge(local.tags, {Name = "Data Lake VPC Endpoint"})
# }
