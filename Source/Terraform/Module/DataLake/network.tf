resource "aws_vpc" "datalake" {
    cidr_block = "172.31.0.0/16"

    tags = merge(local.tags, {Name = "Data Lake VPC"})
}
