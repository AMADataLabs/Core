resource "aws_ecs_cluster" "datalake" {
    name = var.project

    tags = merge(local.tags, {Name = "Data Labs Data Lake ECS Cluster"})
}
