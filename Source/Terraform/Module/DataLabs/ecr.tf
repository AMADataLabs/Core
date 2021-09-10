resource "aws_ecr_repository" "bitbucket" {
    name                 = "datalabs-bitbucket-pipelines"

    tags = merge(local.tags, {Name = "Data Labs BitBucket Pipelines custom build image"})
}
