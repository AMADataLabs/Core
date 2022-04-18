
resource "aws_ecr_repository" "hello_world_java" {
  name = "hello_world_java-${local.environment}"

  tags = merge(local.tags, {Name = "${local.project}-${local.environment}-hello_world_java-ecr"})
}

resource "aws_ecr_repository_policy" "ecr_repository_policy" {
  repository = aws_ecr_repository.hello_world_java.name

  policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "ECR Policy",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "${module.batch_job.job_role.arn}"
        ]
      },
      "Action": [
        "cloudtrail:LookupEvents",
        "ecr:*"
      ]
    }
  ]
}
EOF
}
