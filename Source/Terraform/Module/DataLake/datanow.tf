########## Image Repository ##########

resource "aws_ecr_repository" "datanow" {
    name = "datanow"

    tags = merge(local.tags, {Name = "Data Labs Data Lake DataNow Container Repository"})
}

########## Fargate Service ##########

resource "aws_ecs_service" "datanow" {
    name                                = "DataNow"
    task_definition                     = aws_ecs_task_definition.datanow.arn
    launch_type                         = "FARGATE"
    cluster                             = aws_ecs_cluster.datalake.id
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
            aws_security_group.datanow.id
        ]

        subnets             = [
            aws_subnet.datanow_frontend.id,
            aws_subnet.datanow_backend.id
        ]
    }

    load_balancer {
        target_group_arn    = aws_lb_target_group.datanow.arn
        container_name      = "datanow"
        container_port      = "9047"
    }


    tags = merge(local.tags, {Name = "Data Labs Data Lake DataNow Service"})

    depends_on = [
        aws_ecs_task_definition.datanow,
        aws_lb_target_group.datanow
    ]
}


# module "datanow_task_definition" {
#     source                          = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-ecs-fargate-task-definition.git?ref=feature/templated_container_definitions"
#     task_name                       = "datanow"
#     environment_name                = lower(data.aws_ssm_parameter.account_environment.value)
#     task_role_arn                   = aws_iam_role.datanow_assume.arn
#     execution_role_arn              = aws_iam_role.datanow_execution.arn
#
#     container_definition_vars       = {
#         account_id  = data.aws_caller_identity.account.account_id,
#         region      = data.aws_region.current.name
#         image       = var.datanow_image
#         tag         = var.datanow_version
#     }
#
#     tag_name                        = "${var.project} DataNow Task"
#     tag_environment                 = local.tags["Env"]
#     tag_contact                     = local.tags["Contact"]
#     tag_systemtier                  = local.tags["SystemTier"]
#     tag_drtier                      = local.tags["DRTier"]
#     tag_dataclassification          = local.tags["DataClassification"]
#     tag_budgetcode                  = local.tags["BudgetCode"]
#     tag_owner                       = local.tags["Owner"]
#     tag_projectname                 = var.project
#     tag_notes                       = ""
#     tag_eol                         = local.tags["EOL"]
#     tag_maintwindow                 = local.tags["MaintenanceWindow"]
# }


resource "aws_ecs_task_definition" "datanow" {
    family                      = "datanow"
    cpu                         = 1024
    memory                      = 8192
    requires_compatibilities    = ["FARGATE"]
    network_mode                = "awsvpc"
    task_role_arn               = aws_iam_role.datanow_assume.arn
    execution_role_arn          = aws_iam_role.datanow_execution.arn

    container_definitions       = templatefile(
        "${path.module}/datanow.json",
        {
            account_id  = data.aws_caller_identity.account.account_id,
            region      = data.aws_region.current.name
            image       = var.datanow_image
            tag         = var.datanow_version
        }
    )

    volume {
        name                        = "DataNow"

        efs_volume_configuration {
            file_system_id          = aws_efs_file_system.datanow.id
            root_directory          = "/"
            transit_encryption      = "ENABLED"

            authorization_config {
                access_point_id     = aws_efs_access_point.dremio.id
                iam                 = "ENABLED"
            }
        }
    }

    tags = merge(local.tags, {Name = "Data Lake DataNow ECS Task"})
}


resource "aws_cloudwatch_log_group" "datanow" {
    name = "/ecs/datanow"

    tags = merge(local.tags, {Name = "Data Lake DataNow Log Group"})
}


########## Permissions ##########

resource "aws_iam_role" "datanow_assume" {
    name                = "${var.project}DataNowAssumeRole"

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

resource "aws_iam_role" "datanow_execution" {
    name                = "${var.project}DataNowExecutionRole"

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


resource "aws_iam_role_policy_attachment" "datanow_execution" {
    role        = aws_iam_role.datanow_execution.name
    policy_arn  = data.aws_iam_policy.ecs_task_execution.arn
}


########## Persistent Storage ##########

resource "aws_efs_file_system" "datanow" {
    lifecycle_policy {
        transition_to_ia = "AFTER_30_DAYS"
    }

    tags = merge(local.tags, {Name = "Data Lake DataNow Persistent Storage"})
}


resource "aws_efs_mount_target" "frontend" {
    file_system_id = aws_efs_file_system.datanow.id
    subnet_id      = aws_subnet.datanow_frontend.id

    security_groups = [
        aws_security_group.datanow.id
    ]
}


resource "aws_efs_mount_target" "backend" {
    file_system_id = aws_efs_file_system.datanow.id
    subnet_id      = aws_subnet.datanow_backend.id

    security_groups = [
        aws_security_group.datanow.id
    ]
}


resource "aws_efs_file_system_policy" "datanow" {
  file_system_id = aws_efs_file_system.datanow.id

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Id": "DataNow",
    "Statement": [
        {
            "Sid": "DataNow",
            "Effect": "Allow",
            "Principal": {
                "AWS": "${aws_iam_role.datanow_assume.arn}"
            },
            "Resource": "${aws_efs_file_system.datanow.arn}",
            "Action": [
                "elasticfilesystem:ClientMount",
                "elasticfilesystem:ClientWrite"
            ]
        }
    ]
}
POLICY
}


resource "aws_efs_access_point" "dremio" {
    file_system_id      = aws_efs_file_system.datanow.id

    posix_user {
        uid             = 999
        gid             = 999
        secondary_gids  = []
    }

    root_directory {
        path = "/dremio"

        creation_info {
            owner_uid   = 999
            owner_gid   = 999
            permissions = "0755"
        }
    }

    tags = merge(local.tags, {Name = "Data Lake DataNow Dremio Access Point"})
}

########## Networking ##########

resource "aws_security_group" "datanow" {
    name        = "Data Lake DataNow"
    description = "Allow traffic to DataNow"
    vpc_id      = aws_vpc.datalake.id

    ingress {
        description = "HTTP Client"
        from_port   = 9047
        to_port     = 9047
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "HTTP"
        from_port   = 80
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "HTTPS"
        from_port   = 443
        to_port     = 443
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "ODBC/JDBC Client"
        from_port   = 31010
        to_port     = 31010
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "EFS"
        from_port   = 2049
        to_port     = 2049
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = merge(local.tags, {Name = "Data Lake DataNow SG"})
}


resource "aws_subnet" "datanow_frontend" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.10.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake DataNow Frontend Subnet"})
}


resource "aws_route_table_association" "datanow_frontend" {
    subnet_id      = aws_subnet.datanow_frontend.id
    route_table_id = aws_vpc.datalake.default_route_table_id
}


resource "aws_subnet" "datanow_backend" {
    vpc_id            = aws_vpc.datalake.id
    cidr_block        = "172.31.11.0/24"
    availability_zone = "us-east-1b"

    tags = merge(local.tags, {Name = "Data Lake DataNow Backend Subnet"})
}


resource "aws_route_table_association" "datanow_backend" {
    subnet_id      = aws_subnet.datanow_backend.id
    route_table_id = aws_vpc.datalake.default_route_table_id
}


########## Load Balancer ##########

resource "aws_alb" "datanow" {
    name               = "DataNow"
    internal           = false
    load_balancer_type = "application"

    subnets = [
        aws_subnet.datanow_frontend.id,
        aws_subnet.datanow_backend.id,
    ]

    security_groups = [
        aws_security_group.datanow.id,
    ]

    tags = merge(local.tags, {Name = "Data Lake DataNow Load Balancer"})

    depends_on = [aws_internet_gateway.datalake]
}


resource "aws_lb_target_group" "datanow" {
    name        = "${var.project}DataNow"
    port        = 9047
    protocol    = "HTTP"
    target_type = "ip"
    vpc_id      = aws_vpc.datalake.id

    health_check {
        enabled             = true
        path                = "/apiv2/server_status"
        healthy_threshold   = 5
        unhealthy_threshold = 2
    }

    depends_on = [aws_alb.datanow]
}


resource "aws_alb_listener" "datanow-https" {
  load_balancer_arn = aws_alb.datanow.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = data.aws_acm_certificate.amaaws.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.datanow.arn
  }
}
