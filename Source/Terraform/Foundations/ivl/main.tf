### VPC ###

resource "aws_vpc" "foundations" {
    cidr_block              = "172.31.0.0/16"
    enable_dns_hostnames    = true

    tags = merge(local.tags, {Name = "Foundations VPC"})
}


### Internet Gateway ###

resource "aws_internet_gateway" "foundations" {
    vpc_id = aws_vpc.foundations.id

    tags = merge(local.tags, {Name = "Foundations Internet Gateway"})
}


### NAT Gateway ###

resource "aws_eip" "nat_gateway" {
    vpc = true

    tags = merge(local.tags, {Name = "Foundations NAT Gateway IP"})
}

resource "aws_nat_gateway" "foundations" {
  allocation_id = aws_eip.nat_gateway.id
  subnet_id     = aws_subnet.foundations_public1.id

  depends_on = [aws_internet_gateway.foundations]

  tags = merge(local.tags, {Name = "Foundations NAT Gateway"})
}


### Routes ###

resource "aws_route_table" "foundations_public" {
    vpc_id = aws_vpc.foundations.id

    tags = merge(local.tags, {Name = "Foundations Public Route Table"})
}


resource "aws_route" "foundations_public" {
    route_table_id              = aws_route_table.foundations_public.id
    destination_cidr_block      = "0.0.0.0/0"
    gateway_id                  = aws_internet_gateway.foundations.id
}

resource "aws_route_table" "foundations_private" {
    vpc_id = aws_vpc.foundations.id

    tags = merge(local.tags, {Name = "Foundations Private Route Table"})
}


resource "aws_route" "foundations_private" {
    route_table_id              = aws_route_table.foundations_private.id
    destination_cidr_block      = "0.0.0.0/0"
    nat_gateway_id                = aws_nat_gateway.foundations.id
}


### Subnets ###

resource "aws_subnet" "foundations_public1" {
    vpc_id                  = aws_vpc.foundations.id
    cidr_block              = "172.31.10.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Foundations Public Subnet 1"})
}

resource "aws_route_table_association" "foundations_public1" {
    subnet_id      = aws_subnet.foundations_public1.id
    route_table_id = aws_route_table.foundations_public.id
}

resource "aws_subnet" "foundations_public2" {
    vpc_id            = aws_vpc.foundations.id
    cidr_block        = "172.31.11.0/24"
    availability_zone = "us-east-1b"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Foundations Public Subnet 2"})
}

resource "aws_route_table_association" "foundations_public2" {
    subnet_id      = aws_subnet.foundations_public2.id
    route_table_id = aws_route_table.foundations_public.id
}

resource "aws_subnet" "foundations_private1" {
    vpc_id                  = aws_vpc.foundations.id
    cidr_block              = "172.31.12.0/24"
    availability_zone       = "us-east-1c"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Foundations Private Subnet 1"})
}

resource "aws_route_table_association" "foundations_private1" {
    subnet_id      = aws_subnet.foundations_private1.id
    route_table_id = aws_route_table.foundations_private.id
}

resource "aws_subnet" "foundations_private2" {
    vpc_id                  = aws_vpc.foundations.id
    cidr_block              = "172.31.13.0/24"
    availability_zone       = "us-east-1d"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Foundations Private Subnet 2"})
}

resource "aws_route_table_association" "foundations_private2" {
    subnet_id      = aws_subnet.foundations_private2.id
    route_table_id = aws_route_table.foundations_private.id
}

### Bastion ###

resource "aws_key_pair" "bastion_key" {
    key_name   = "DataLakeBastionKey"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMdCgPAcG2MsIQF7Zds/qaGTMNjWNeYIQXdwb+HvtSqJrtRDXo/XZUu6m4MUrFs0n6vDleSfAafp3xZ9VLLQN/6vVIuJW9GDRiJl1fqPessQxKKFGqJuSv+TrZ20RiUkUpGOmUKcBB6N1Hwkqped2DfTYIX9If3i4OKgdFETg8U2jlxFixvOtruSosm8g/xsHC2Xmnvv4VTc1DwWECARVYGRFUIdIdy/PNkIhzWGNp1aDs5ALzpZ5WhtqkzSBr49tYbALORs/DcN5CV6RSZ3vaVvcXoQrweDl6Cd5eCTiPxU8xsZGZFFPwWK9VXXrLJkpSMeqZmHacPNRAp+zd2zOZ"

    tags = merge(local.tags, {Name = "Foundations Bastion Key"})
}


resource "aws_security_group" "foundations_bastion" {
  name        = "DataLake-sbx-bastion-sg"
  description = "Allow SSH inbound traffic"
  vpc_id      = aws_vpc.foundations.id

  ingress {
    description = "SSH traffic"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "VPC traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["172.31.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

    tags = merge(local.tags, {Name = "Temporary development box SG"})
}


resource "aws_instance" "foundations_bastion" {
    ami                             = data.aws_ami.foundations_bastion.id
    instance_type                   = "t2.micro"
    key_name                        = aws_key_pair.bastion_key.key_name
    subnet_id                       = aws_subnet.foundations_public1.id
    vpc_security_group_ids          = [aws_security_group.foundations_bastion.id]
    associate_public_ip_address     = true

    tags = merge(local.tags, {Name = "Foundations Bastion", OS = "Ubuntu 18.04"})
    volume_tags = merge(local.tags, {Name = "Foundations Bastion", OS = "Ubuntu 18.04"})
}


data "aws_ami" "ubuntu" {
    most_recent = true

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20200821.1"]
        }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }

    owners = ["099720109477"] # Canonical
}


### API Gateway ###

module "apigw_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"
  name        = "${local.project}-${local.environment}-apigw-sg"
  description = "Security group for API Gateway VPC interfaces"
  vpc_id      = aws_vpc.foundations.id

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "User-service ports"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = "-1"
      to_port     = "-1"
      protocol    = "-1"
      description = "outbound ports"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = merge(local.tags, {Name = "${local.project}-${local.environment}-foundations-sg"})
}


resource "aws_vpc_endpoint" "apigw" {
  vpc_id            = aws_vpc.foundations.id
  service_name      = "com.amazonaws.${local.region}.execute-api"
  vpc_endpoint_type = "Interface"

  security_group_ids = [
    module.apigw_sg.security_group_id
  ]

  subnet_ids        = [aws_subnet.foundations_private1.id, aws_subnet.foundations_private2.id]

  private_dns_enabled = true

  tags = merge(local.tags, {Name = "${local.environment}-execute-api_vpc_endpoint"})
}
