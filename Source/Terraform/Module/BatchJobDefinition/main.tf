resource "aws_batch_job_definition" "job_definition" {
  name = "${var.tag_projectname}-${var.environment}-${var.name}-jd"
  type = "container"

  platform_capabilities = [
    "FARGATE"
  ]

  container_properties = data.template_file.container_properties.rendered

  tags = merge(local.tags,  {Name = upper("${var.tag_projectname}-${var.environment}-${var.name}-jd")})
}


data "template_file" "container_properties" {
  template = file("${path.module}/files/container_properties.json")

  vars = {
      ecr_account = var.ecr_account
      region = local.region
      image = var.image
      version = var.image_version
      command = jsonencode(var.command)
      environment = var.environment_vars
      job_role = aws_iam_role.job_role.arn
      service_role = aws_iam_role.service_role.arn
      volumes = var.volumes
      mount_points = var.mount_points
      readonly_filesystem = var.readonly_filesystem
      ulimits = var.ulimits
      user = var.user
      resource_requirements = var.resource_requirements
      linux_parameters = var.linux_parameters
      log_configuration = var.log_configuration
      secrets = var.secrets
      service_role = aws_iam_role.service_role.arn
      job_role = aws_iam_role.job_role.arn
  }
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
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

  tags = merge(local.tags,  {Name = upper("${var.tag_projectname}-${var.environment}-${var.name}-service-role")})
}

resource "aws_iam_role" "job_role" {
  name               = "${var.tag_projectname}-${var.environment}-${var.name}-job-role"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
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

  tags = merge(local.tags,  {Name = upper("${var.tag_projectname}-${var.environment}-${var.name}-job-role")})
}

resource "aws_iam_role_policy_attachment" "service_ecs_policy" {
  role       = aws_iam_role.service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "job_ssm_policy" {
  role       = aws_iam_role.job_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "job_batch_policy" {
  role       = aws_iam_role.job_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}
