resource "aws_batch_compute_environment" "compute_environment" {
  compute_environment_name = "${var.tag_projectname}-${var.environment}-${var.name}-${var.name}"

  compute_resources {
    max_vcpus          = var.max_vcpus
    security_group_ids = var.security_groups
    subnets            = var.subnets
    type               = "FARGATE"
  }

  service_role = aws_iam_role.service_role.arn
  type         = "MANAGED"

  tags = merge(local.tags, { Name = upper("${var.tag_projectname}-${var.environment}-${var.name}-${var.name}-ce") })

  depends_on = [aws_iam_role_policy_attachment.service_ecs_policy]
}

resource "aws_iam_role" "service_role" {
  name = "${var.tag_projectname}-${var.environment}-${var.name}-service-role"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "batch.amazonaws.com",
                    "ecs-tasks.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

  tags = merge(local.tags, { Name = upper("${var.tag_projectname}-${var.environment}-${var.name}-service-role") })
}

resource "aws_iam_role_policy_attachment" "service_ecs_policy" {
  role       = aws_iam_role.service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "service_batch_policy" {
  role       = aws_iam_role.service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}
