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
