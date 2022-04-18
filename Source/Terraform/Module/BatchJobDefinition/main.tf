resource "aws_batch_job_definition" "job_definition" {
  name = "${var.project}-${var.environment}-${var.name}"
  type = "container"

  platform_capabilities = [
    "FARGATE"
  ]

  container_properties = data.template_file.container_properties.rendered

  tags = merge(local.tags, { Name = upper("${var.project}-${var.environment}-${var.name}-jd") })
}


data "template_file" "container_properties" {
  template = file("${path.module}/files/container_properties.json")

  vars = {
    ecr_account           = var.ecr_account
    region                = local.region
    image                 = var.image
    version               = var.image_version
    command               = jsonencode(var.command)
    environment           = var.environment_vars
    job_role              = aws_iam_role.job_role.arn
    service_role          = var.service_role
    volumes               = var.volumes
    mount_points          = var.mount_points
    readonly_filesystem   = var.readonly_filesystem
    ulimits               = var.ulimits
    user                  = var.user
    resource_requirements = var.resource_requirements
    linux_parameters      = var.linux_parameters
    log_configuration     = var.log_configuration
    secrets               = var.secrets
  }
}

resource "aws_iam_role" "job_role" {
  name               = "${var.project}-${var.environment}-${var.name}-job-role"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": [
                    "ecs-tasks.amazonaws.com"
                ]
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

  tags = merge(local.tags, { Name = upper("${var.project}-${var.environment}-${var.name}-job-role") })
}


data "template_file" "policy" {
  template = file("policies/${var.name}.json")
  vars = var.policy_vars
}

resource "aws_iam_policy" "policy" {
  name        = "${var.project}-${var.environment}-${var.name}-job-policy"
  path        = "/"
  description = "IAM policy for ${var.name} jobs"

  policy = data.template_file.policy.rendered
}

resource "aws_iam_role_policy_attachment" "policy" {
  role       = aws_iam_role.job_role.name
  policy_arn = aws_iam_policy.policy.arn
}
