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


resource "aws_ecs_task_definition" "datanow" {
    family                      = "datanow"
    cpu                         = 1024
    memory                      = 8192
    requires_compatibilities    = ["FARGATE"]
    network_mode                = "awsvpc"
    task_role_arn               = aws_iam_role.datanow_assume.arn
    execution_role_arn          = aws_iam_role.datanow_execution.arn

    container_definitions       = jsonencode([
        {
            name                    = "datanow"
            image                   = "${data.aws_caller_identity.account.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/datanow:1.0.0"
            cpu                     = 0
            environment             = []
            essential               = true
            volumesFrom             = []

            ulimits = [
                {
                    name            = "nofile",
                    softLimit       = 65536,
                    hardLimit       = 1048576
                }
            ]

            portMappings = [
                {
                    containerPort   = 9047
                    hostPort        = 9047
                    protocol        = "tcp"
                },
                {
                    containerPort   = 31010
                    hostPort        = 31010
                    protocol        = "tcp"
                },
                {
                    containerPort   = 45678
                    hostPort        = 45678
                    protocol        = "tcp"
                }
            ]

            mountPoints = [
                {
                    sourceVolume    = "DataNow",
                    containerPath   = "/opt/dremio/data"
                    readOnly        = false
                }
            ]

            logConfiguration = {
                logDriver                   = "awslogs"

                options = {
                    awslogs-region          = data.aws_region.current.name
                    awslogs-group           = "/ecs/datanow"
                    awslogs-stream-prefix   = "ecs"
                }
            }
        }
    ])

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


resource "aws_route53_record" "datanow" {
    zone_id         = data.aws_route53_zone.amaaws.zone_id
    name            = "datanow.amaaws.org"
    type            = "A"

    alias {
        name                    = aws_alb.datanow.dns_name
        zone_id                 = aws_alb.datanow.zone_id
        evaluate_target_health  = true
    }
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
