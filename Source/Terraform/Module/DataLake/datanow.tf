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
    execution_role_arn          = aws_iam_role.datanow.arn

    container_definitions       = <<EOF
[
    {
        "name": "datanow",
        "image": "${data.aws_caller_identity.account.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/datanow:1.0.0",

        "ulimits": [
            {
                "name": "nofile",
                "softLimit": 65536,
                "hardLimit": 1048576
            }
        ],

        "portMappings": [
            {
                "containerPort": 9047
            },
            {
                "containerPort": 31010
            },
            {
                "containerPort": 45678
            }
        ],

        "logConfiguration": {
            "logDriver": "awslogs",

            "options": {
                "awslogs-region": "${data.aws_region.current.name}",
                "awslogs-group": "/ecs/datanow",
                "awslogs-stream-prefix": "ecs"
            }
        }
    }
]
EOF

    tags = merge(local.tags, {Name = "Data Lake DataNow ECS Task"})
}


resource "aws_cloudwatch_log_group" "datanow" {
    name = "/ecs/datanow"

    tags = merge(local.tags, {Name = "Data Lake DataNow Log Group"})
}


########## Permissions ##########

resource "aws_iam_role" "datanow" {
    name                = "${var.project}DataNow"

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


resource "aws_iam_role_policy_attachment" "ecs-task-execution-role" {
    role        = aws_iam_role.datanow.name
    policy_arn  = data.aws_iam_policy.ecs_task_execution.arn
}


########## Persistent Storage ##########

resource "aws_efs_file_system" "datanow" {
    lifecycle_policy {
        transition_to_ia = "AFTER_30_DAYS"
    }

    tags = merge(local.tags, {Name = "Data Lake DataNow Persistent Storage"})
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
