resource "aws_security_group" "lineage" {
    name        = "Data Lake Lineage"
    description = "Allow inbound traffic to Neptune"
    vpc_id      = aws_vpc.datalake.id

    ingress {
        description = "Gremlin"
        from_port   = 8182
        to_port     = 8182
        protocol    = "tcp"
        # cidr_blocks = [aws_vpc.development.cidr_block]
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = merge(local.tags, {Name = "Data Lake Lineage SG"})
}


resource "aws_subnet" "lineage_frontend" {
    vpc_id            = aws_vpc.datalake.id
    cidr_block        = "172.31.0.0/24"
    availability_zone = "us-east-1a"

    tags = merge(local.tags, {Name = "Data Lake Lineage Fronend Subnet"})
}


resource "aws_route_table_association" "lineage_frontend" {
    subnet_id      = aws_subnet.lineage_frontend.id
    route_table_id = aws_vpc.datalake.default_route_table_id
}


resource "aws_subnet" "lineage_backend" {
    vpc_id            = aws_vpc.datalake.id
    cidr_block        = "172.31.1.0/24"
    availability_zone = "us-east-1b"

    tags = merge(local.tags, {Name = "Data Lake Lineage Backend Subnet"})
}


resource "aws_route_table_association" "lineage_backend" {
    subnet_id      = aws_subnet.lineage_backend.id
    route_table_id = aws_vpc.datalake.default_route_table_id
}


resource "aws_neptune_subnet_group" "lineage" {
    name       = "datalabs-datalake-lineage"
    subnet_ids = [aws_subnet.lineage_frontend.id, aws_subnet.lineage_backend.id]

    tags = merge(local.tags, {Name = "Data Lake Lineage Subnet Group"})
}


resource "aws_neptune_cluster" "linage_cluster" {
    cluster_identifier                  = "datalabs-lineage"
    skip_final_snapshot                 = true
    iam_database_authentication_enabled = true
    apply_immediately                   = true
    deletion_protection                 = false
    vpc_security_group_ids              = [aws_security_group.lineage.id]
    neptune_subnet_group_name           = aws_neptune_subnet_group.lineage.name

    tags = merge(local.tags, {Name = "Data Labs Data Lake Lineage DB Cluster"})
}

resource "aws_neptune_cluster_instance" "lineage" {
    identifier                          = "lineage"
    cluster_identifier                  = aws_neptune_cluster.linage_cluster.id
    instance_class                      = "db.t3.medium"
    apply_immediately                   = true
    neptune_subnet_group_name           = aws_neptune_subnet_group.lineage.name

    tags = merge(local.tags, {Name = "Data Labs Data Lake Lineage DB Instance"})
}
