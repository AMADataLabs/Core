#####################################################################
# Datalake - ECS Service and Task Definitions             #
#####################################################################

resource "aws_ecs_service" "etcd" {
    name                                = "etcd"
    task_definition                     = module.etcd_task_definition.aws_ecs_task_definition_td_arn
    launch_type                         = "FARGATE"
    cluster                             = module.datalake_ecs_cluster.ecs_cluster_id
    desired_count                       = 1
    platform_version                    = "1.4.0"
    health_check_grace_period_seconds   = 0
    propagate_tags                      = "TASK_DEFINITION"

    deployment_controller {
        type                = "ECS"
    }

    timeouts {}

    network_configuration {
        assign_public_ip    = true

        security_groups     = [
            module.etcd_sg.security_group_id
        ]

        subnets             = [
            aws_subnet.datalake_public1.id,
            aws_subnet.datalake_public2.id
        ]
    }

    load_balancer {
        target_group_arn    = aws_lb_target_group.etcd.arn
        container_name      = "etcd"
        container_port      = "2379"
    }


    tags = merge(local.tags, {Name = "Data Labs Data Lake etcd Service"})

    depends_on = [
        module.etcd_task_definition,
        aws_lb_target_group.etcd
    ]
}


module "etcd_task_definition" {
    source                          = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-ecs-fargate-task-definition.git?ref=2.0.0"
    task_name                       = "etcd"
    environment_name                = var.environment
    execution_role_arn              = aws_iam_role.etcd_execution.arn
    task_role_arn                   = aws_iam_role.etcd_task.arn
    container_cpu                   = 1024
    container_memory                = 8192

    container_definition_vars       = {
        region      = var.region
    }

    volume = [
        {
            name                        = "etcd"

            efs_volume_configuration    = [
                {
                    "file_system_id":       module.etcd_efs.filesystem_id
                    "root_directory":       "/"
                    "transit_encryption":   "ENABLED"

                    "authorization_config": {
                        "access_point_id":  module.etcd_efs.access_point_id
                        "iam":              "ENABLED"
                    }
                }
            ]
        }
    ]

    tag_name                        = "${var.project} etcd Task"
    tag_environment                   = var.environment
    tag_contact                       = local.contact
    tag_budgetcode                    = local.budget_code
    tag_owner                         = local.owner
    tag_projectname                   = local.project
    tag_systemtier                    = local.tier
    tag_drtier                        = local.tier
    tag_dataclassification            = local.na
    tag_notes                         = local.na
    tag_eol                           = local.na
    tag_maintwindow                   = local.na
    tags = {
        Group                               = local.group
        Department                          = local.department
    }
}


resource "aws_alb" "etcd" {
    name               = "etcd"
    internal           = false  # Internet-facing. Requires an Internet Gateway
    load_balancer_type = "application"

    subnets = [
        aws_subnet.datalake_public1.id,
        aws_subnet.datalake_public2.id
    ]

    security_groups = [
        module.etcd_sg.security_group_id,
    ]

    tags = merge(local.tags, {Name = "Data Lake etcd Load Balancer"})

    depends_on = [aws_internet_gateway.datalake]
}


resource "aws_alb_listener" "etcd-https" {
  load_balancer_arn = aws_alb.etcd.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = data.aws_acm_certificate.amaaws.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.etcd.arn
  }
}


resource "aws_lb_target_group" "etcd" {
    name        = "${var.project}Etcd"
    port        = 2379
    protocol    = "HTTP"
    target_type = "ip"
    vpc_id      = aws_vpc.datalake.id

    health_check {
        enabled             = true
        path                = "/health"
        healthy_threshold   = 5
        unhealthy_threshold = 2
    }
}


module "etcd_sg" {
    source = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-security-group.git?ref=1.0.0"

    name        = "${lower(var.project)}-${var.environment}-etcd"
    description = "Security group for Datanow"
    vpc_id      = aws_vpc.datalake.id

    ingress_with_cidr_blocks = [
        {
            description = "HTTP Client"
            from_port   = "2379"
            to_port     = "2379"
            protocol    = "tcp"
            cidr_blocks = "0.0.0.0/0"
        },
        {
            description = "HTTPS"
            from_port   = "443"
            to_port     = "443"
            protocol    = "tcp"
            cidr_blocks = "0.0.0.0/0"
        },
        {
            description = "EFS"
            from_port   = "2049"
            to_port     = "2049"
            protocol    = "tcp"
            cidr_blocks = "0.0.0.0/0"
        }
    ]

    egress_with_cidr_blocks = [
        {
            description = "Outbound Ports"
            from_port   = "0"
            to_port     = "0"
            protocol    = "-1"
            cidr_blocks = "0.0.0.0/0"
        }
    ]

    tags = merge(local.tags, {Name = "Data Lake etcd Security Group"})
}


resource "aws_cloudwatch_log_group" "etcd" {
    name = "/ecs/etcd"

    tags = merge(local.tags, {Name = "Data Lake etcd Log Group"})
}


resource "aws_iam_role" "etcd_task" {
    name                = "${var.project}EtcdAssumeRole"

    assume_role_policy  = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_role" "etcd_execution" {
    name                = "${var.project}EtcdExecutionRole"

    assume_role_policy  = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}


resource "aws_iam_policy" "etcd_task_execution" {
    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "etcd_execution" {
    role        = aws_iam_role.etcd_execution.name
    policy_arn  = aws_iam_policy.etcd_task_execution.arn
}


#####################################################################
# Datalake - EFS Volume                                             #
#####################################################################

module "etcd_efs" {
    source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-efs.git?ref=2.0.0"
    performance_mode = "generalPurpose"
    transition_to_ia = "AFTER_14_DAYS"
    posix_user_gid   = 999
    posix_user_uid   = 999
    path_permissions = 755
    access_point_path = "/etcd"
    app_name                         = lower(var.project)
    app_environment                  = var.environment
    subnet_ids                       = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
    security_groups                  = [module.etcd_sg.security_group_id]

    tag_name                         = "${var.project}-${var.environment}-etcd-efs"
    tag_environment                   = var.environment
    tag_contact                       = local.contact
    tag_budgetcode                    = local.budget_code
    tag_owner                         = local.owner
    tag_projectname                   = local.project
    tag_systemtier                    = local.tier
    tag_drtier                        = local.tier
    tag_dataclassification            = local.na
    tag_notes                         = local.na
    tag_eol                           = local.na
    tag_maintwindow                   = local.na
    tags = {
        Group                               = local.group
        Department                          = local.department
    }
}
