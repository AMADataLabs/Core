resource "aws_batch_job_definition" "job_definition" {
  name = "${var.tag_projectname}-${var.environment}-${var.task}-jd"
  type = "container"

  platform_capabilities = [
    "FARGATE",
  ]

  container_properties = data.template_file.job_definition.rendered

  tags = merge(local.tags,  {Name = "upper(${var.project}-${local.environment}-${var.task}-jd")})
}


data "template_file" "job-definitions" {
  template = file("job-definitions/${var.task}.json")

  vars = var.container_properties_vars
}


resource "aws_iam_role" "service_role" {
  name = "${var.lambda_name}-iam-for-lambda"

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

  tags = merge(local.tags,  {Name = "upper(${var.project}-${local.environment}-${var.task}-job-exe-role")})
}

resource "aws_iam_role" "job_role" {
  name               = "${var.tag_projectname}-${var.environment}-${var.task_name}-job-role"
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

  tags = merge(local.tags,  {Name = "upper(${var.project}-${local.environment}-${var.task}-job-role")})
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
