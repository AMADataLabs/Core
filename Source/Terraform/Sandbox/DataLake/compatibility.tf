### VPC ###

resource "aws_vpc" "datalake" {
    cidr_block              = "172.31.0.0/16"
    enable_dns_hostnames    = true

    tags = merge(local.tags, {Name = "Data Lake VPC"})
}


### Internet Gateway ###

resource "aws_internet_gateway" "datalake" {
    vpc_id = aws_vpc.datalake.id

    tags = merge(local.tags, {Name = "Data Lake Internet Gateway"})
}


### NAT Gateway ###

resource "aws_eip" "nat_gateway" {
    vpc = true

    tags = merge(local.tags, {Name = "Data Lake NAT Gateway IP"})
}

resource "aws_nat_gateway" "datalake" {
  allocation_id = aws_eip.nat_gateway.id
  subnet_id     = aws_subnet.datalake_public1.id

  depends_on = [aws_internet_gateway.datalake]

  tags = merge(local.tags, {Name = "Data Lake NAT Gateway"})
}


### Routes ###

resource "aws_route_table" "datalake_public" {
    vpc_id = aws_vpc.datalake.id

    tags = merge(local.tags, {Name = "Data Lake Public Route Table"})
}


resource "aws_route" "datalake_public" {
    route_table_id              = aws_route_table.datalake_public.id
    destination_cidr_block      = "0.0.0.0/0"
    gateway_id                  = aws_internet_gateway.datalake.id
}

resource "aws_route_table" "datalake_private" {
    vpc_id = aws_vpc.datalake.id

    tags = merge(local.tags, {Name = "Data Lake Private Route Table"})
}


resource "aws_route" "datalake_private" {
    route_table_id              = aws_route_table.datalake_private.id
    destination_cidr_block      = "0.0.0.0/0"
    nat_gateway_id                = aws_nat_gateway.datalake.id
}


### Subnets ###

resource "aws_subnet" "datalake_public1" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.10.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Public Subnet 1"})
}

resource "aws_route_table_association" "datalake_public1" {
    subnet_id      = aws_subnet.datalake_public1.id
    route_table_id = aws_route_table.datalake_public.id
}

resource "aws_subnet" "datalake_public2" {
    vpc_id            = aws_vpc.datalake.id
    cidr_block        = "172.31.11.0/24"
    availability_zone = "us-east-1b"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Public Subnet 2"})
}

resource "aws_route_table_association" "datalake_public2" {
    subnet_id      = aws_subnet.datalake_public2.id
    route_table_id = aws_route_table.datalake_public.id
}

resource "aws_subnet" "datalake_private1" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.12.0/24"
    availability_zone       = "us-east-1c"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Private Subnet 1"})
}

resource "aws_route_table_association" "datalake_private1" {
    subnet_id      = aws_subnet.datalake_private1.id
    route_table_id = aws_route_table.datalake_private.id
}

resource "aws_subnet" "datalake_private2" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.13.0/24"
    availability_zone       = "us-east-1d"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Private Subnet 2"})
}

resource "aws_route_table_association" "datalake_private2" {
    subnet_id      = aws_subnet.datalake_private2.id
    route_table_id = aws_route_table.datalake_private.id
}
