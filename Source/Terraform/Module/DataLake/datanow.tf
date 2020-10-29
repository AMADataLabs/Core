########## Fargate Service ##########

resource "aws_ecs_service" "datanow" {
    name                    = "datanow"
    task_definition         = aws_ecs_task_definition.datanow.arn
    launch_type             = "FARGATE"
    cluster                 = aws_ecs_cluster.datalake.id
    desired_count           = 1

    network_configuration {
        assign_public_ip    = false

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
        container_port      = "80"
    }

    tags = merge(local.tags, {Name = "Data Labs Data Lake DataNow Service"})
}


resource "aws_ecs_task_definition" "datanow" {
family                          = "datanow"
    cpu                         = 256
    memory                      = 512
    requires_compatibilities    = ["FARGATE"]
    network_mode                = "awsvpc"
    execution_role_arn = aws_iam_role.datanow.arn

    container_definitions = <<EOF
[
    {
        "name": "datanow",
        "image": "${data.aws_caller_identity.account.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/datanow:1.0.0",
        "entryPoint": ["/opt/dremio"],
        "command": ["bin/dremio", "start-fg"],

        "portMappings": [
            {
                "containerPort": 9047
            },
            {
                "containerPort": 31010
            },
            {
                "containerPort": 45678
            },
            {
                "containerPort": 80
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
}


########## Permissions ##########

resource "aws_iam_role" "datanow" {
    name                = "${var.project}DataNow"

    assume_role_policy = <<EOF
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


# Networking

resource "aws_security_group" "datanow" {
    name        = "Data Lake DataNow"
    description = "Allow inbound traffic to DataNow"
    vpc_id      = aws_vpc.datalake.id

    ingress {
        description = "HTTP Requests"
        from_port   = 80
        to_port     = 80
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
    vpc_id            = aws_vpc.datalake.id
    cidr_block        = "172.31.10.0/24"
    availability_zone = "us-east-1a"

    tags = merge(local.tags, {Name = "Data Lake DataNow Subnet"})
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

resource "aws_lb_target_group" "datanow" {
    name        = "${var.project}DataNow"
    port        = 80
    protocol    = "HTTP"
    target_type = "ip"
    vpc_id      = aws_vpc.datalake.id

    health_check {
        enabled = true
        path    = "/"
    }

    depends_on = [aws_alb.datanow]
}

resource "aws_alb" "datanow" {
    name               = "${var.project}DataNow"
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

resource "aws_alb_listener" "datalake" {
  load_balancer_arn = aws_alb.datanow.arn
  port              = "443"
  protocol          = "HTTPS"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.datanow.arn
  }
}
