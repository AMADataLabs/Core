provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


data "aws_caller_identity" "account" {}


#####################################################################
# Datalake - VPC                                                    #
#####################################################################

resource "aws_vpc" "datalake" {
    cidr_block              = "172.31.0.0/16"
    enable_dns_hostnames    = true

    tags = merge(local.tags, {Name = "Data Lake VPC"})
}


### Internet Gateway ###

resource "aws_internet_gateway" "datalake" {
    vpc_id = aws_vpc.datalake.id

    tags = merge(local.tags, {Name = "Data Lake Internet Gateway"})
}


### Routes ###

resource "aws_route_table" "datalake_public" {
  vpc_id = aws_vpc.datalake.id

    tags = merge(local.tags, {Name = "Data Lake Public Route Table"})
}


resource "aws_route" "datalake_public" {
    route_table_id              = aws_route_table.datalake_public.id
    destination_cidr_block      = "0.0.0.0/0"
    gateway_id                  = aws_internet_gateway.datalake.id
}


### Subnets ###

resource "aws_subnet" "datalake_public1" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.10.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Public Subnet 1"})
}

resource "aws_route_table_association" "datalake_public1" {
    subnet_id      = aws_subnet.datalake_public1.id
    route_table_id = aws_route_table.datalake_public.id
}


resource "aws_subnet" "datalake_public2" {
    vpc_id            = aws_vpc.datalake.id
    cidr_block        = "172.31.11.0/24"
    availability_zone = "us-east-1b"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Public Subnet 2"})
}

resource "aws_route_table_association" "datalake_public2" {
    subnet_id      = aws_subnet.datalake_public2.id
    route_table_id = aws_route_table.datalake_public.id
}


resource "aws_subnet" "datalake_private1" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.12.0/24"
    availability_zone       = "us-east-1c"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Private Subnet 1"})
}

resource "aws_route_table_association" "datalake_private1" {
    subnet_id      = aws_subnet.datalake_private1.id
    route_table_id = aws_vpc.datalake.default_route_table_id
}


resource "aws_subnet" "datalake_private2" {
    vpc_id                  = aws_vpc.datalake.id
    cidr_block              = "172.31.13.0/24"
    availability_zone       = "us-east-1d"
    map_public_ip_on_launch = true

    tags = merge(local.tags, {Name = "Data Lake Private Subnet 2"})
}

resource "aws_route_table_association" "datalake_private2" {
    subnet_id      = aws_subnet.datalake_private2.id
    route_table_id = aws_vpc.datalake.default_route_table_id
}


### NAT Gateway ###
resource "aws_eip" "nat_gateway" {
    vpc = true

    tags = merge(local.tags, {Name = "Data Lake NAT Gateway IP"})
}

resource "aws_nat_gateway" "datalake" {
  allocation_id = aws_eip.nat_gateway.id
  subnet_id     = aws_subnet.datalake_public1.id

  depends_on = [aws_internet_gateway.datalake]

  tags = merge(local.tags, {Name = "Data Lake NAT Gateway"})
}


### VPC Endpoints ###

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.datalake.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.datalake_public.id]

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-s3-vpce"})
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.datalake.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.datalake_public.id]

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-dynamodb-vpce"})
}


resource "aws_vpc_endpoint" "cloudwatch" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-dkr-vpce"})
}


resource "aws_vpc_endpoint" "dkr" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-dkr-vpce"})
}


resource "aws_vpc_endpoint" "ecr" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.ecr.api"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-ecr-vpce"})
}


resource "aws_vpc_endpoint" "ssm" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.ssm"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-ssm-vpce"})
}


resource "aws_vpc_endpoint" "secretsmanager" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.secretsmanager"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-secretsmanager-vpce"})
}


resource "aws_vpc_endpoint" "lambda" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.lambda"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-lambda-vpce"})
}


resource "aws_vpc_endpoint" "sns" {
  vpc_id              = aws_vpc.datalake.id
  private_dns_enabled = true
  service_name        = "com.amazonaws.${var.region}.sns"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = var.outbound_security_groups
  subnet_ids          = local.subnets

  tags = merge(local.tags, {Name = "${var.project}-${var.environment}-lambda-vpce"})
}


# Security Groups

# resource "aws_security_group" "datalake" {
#   name        = "Data Lake"
#   description = "Allow all inbound traffic from bastions and the same security group"
#   vpc_id      = aws_vpc.datalake.id
#
#     ingress {
#         description = "All"
#         from_port   = 0
#         to_port     = 0
#         protocol    = "-1"
#         self        = true
#         security_groups = [aws_security_group.bastion_ssh.id]
#     }
#
#     egress {
#         from_port   = 0
#         to_port     = 0
#         protocol    = "-1"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     tags = merge(local.tags, {Name = "Data Lake"})
# }


module "apigw_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"
  name        = "${var.project}-${var.environment}-apigw-sg"
  description = "Security group for API Gateway VPC interfaces"
  vpc_id      = aws_vpc.datalake.id

  ingress_with_cidr_blocks = [
    {
      from_port   = "-1"
      to_port     = "-1"
      protocol    = "-1"
      description = "User-service ports"
      cidr_blocks = "0.0.0.0/0,10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = "-1"
      to_port     = "-1"
      protocol    = "-1"
      description = "outbound ports"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

}


resource "aws_vpc_endpoint" "apigw" {
  vpc_id            = aws_vpc.datalake.id
  service_name      = "com.amazonaws.${var.region}.execute-api"
  vpc_endpoint_type = "Interface"

  security_group_ids = [
    module.apigw_sg.security_group_id
  ]

  subnet_ids        = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]

  private_dns_enabled = true

  tags = merge(local.tags, {Name = "${var.environment}-execute-api_vpc_endpoint"})
}


#####################################################################
# Datalake - Bastion                                                #
#####################################################################

resource "aws_key_pair" "bastion_key" {
    key_name   = "DataLakeBastionKey"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMdCgPAcG2MsIQF7Zds/qaGTMNjWNeYIQXdwb+HvtSqJrtRDXo/XZUu6m4MUrFs0n6vDleSfAafp3xZ9VLLQN/6vVIuJW9GDRiJl1fqPessQxKKFGqJuSv+TrZ20RiUkUpGOmUKcBB6N1Hwkqped2DfTYIX9If3i4OKgdFETg8U2jlxFixvOtruSosm8g/xsHC2Xmnvv4VTc1DwWECARVYGRFUIdIdy/PNkIhzWGNp1aDs5ALzpZ5WhtqkzSBr49tYbALORs/DcN5CV6RSZ3vaVvcXoQrweDl6Cd5eCTiPxU8xsZGZFFPwWK9VXXrLJkpSMeqZmHacPNRAp+zd2zOZ"

    tags = merge(local.tags, {Name = "Data Lake Bastion Key"})
}


resource "aws_security_group" "datalake_bastion" {
  name        = "DataLake-sbx-bastion-sg"
  description = "Allow SSH inbound traffic"
  vpc_id      = aws_vpc.datalake.id

  ingress {
    description = "SSH traffic"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "VPC traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["172.31.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

    tags = merge(local.tags, {Name = "Temporary development box SG"})
}


# resource "aws_security_group" "bastion_ssh" {
#   name        = "Bastion SSH"
#   description = "Allow SSH inbound traffic to bastions"
#   vpc_id      = aws_vpc.datalake.id
#
#     ingress {
#         description = "SSH"
#         from_port   = 22
#         to_port     = 22
#         protocol    = "tcp"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     ingress {
#       description = "SNMP"
#       from_port   = 161
#       to_port     = 161
#       protocol    = "udp"
#       cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     egress {
#         from_port   = 0
#         to_port     = 0
#         protocol    = "-1"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     tags = merge(local.tags, {Name = "Bastion SG"})
# }
#
#
# resource "aws_subnet" "bastion" {
#   vpc_id            = aws_vpc.datalake.id
#   cidr_block        = "172.31.100.0/24"
#   # availability_zone = "us-west-2a"
#
#     tags = merge(local.tags, {Name = "Data Lake Bastion Subnet"})
# }
#
#
# resource "aws_route_table_association" "bastion" {
#     subnet_id      = aws_subnet.bastion.id
#     route_table_id = aws_vpc.datalake.default_route_table_id
# }
#
#
resource "aws_instance" "datalake_bastion" {
    ami                             = data.aws_ami.datalake_bastion.id
    instance_type                   = "t2.micro"
    key_name                        = aws_key_pair.bastion_key.key_name
    subnet_id                       = aws_subnet.datalake_public1.id
    vpc_security_group_ids          = [aws_security_group.datalake_bastion.id]
    associate_public_ip_address     = true

    tags = merge(local.tags, {Name = "Data Lake Bastion", OS = "Ubuntu 18.04"})
    volume_tags = merge(local.tags, {Name = "Data Lake Bastion", OS = "Ubuntu 18.04"})
}


data "aws_ami" "datalake_bastion" {
    most_recent = true

    filter {
        name   = "name"
        values = ["Temporary development box 2021-08-09"]
        }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }

    owners = [data.aws_caller_identity.account.account_id]
}


# resource "aws_instance" "test" {
#     ami                             = data.aws_ami.ubuntu.id
#     instance_type                   = "t2.micro"
#     key_name                        = aws_key_pair.bastion_key.key_name
#     subnet_id                       = aws_subnet.datanow1.id
#     vpc_security_group_ids          = [module.datanow_sg.security_group_id]
#     associate_public_ip_address     = true
#
#     tags = merge(local.tags, {Name = "Data Lake SG Test", OS = "Ubuntu 18.04"})
#     volume_tags = merge(local.tags, {Name = "Data Lake SG Test", OS = "Ubuntu 18.04"})
# }


# data "aws_ami" "ubuntu" {
#     most_recent = true
#
#     filter {
#         name   = "name"
#         values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20200821.1"]
#         }
#
#     filter {
#         name   = "virtualization-type"
#         values = ["hvm"]
#     }
#
#     owners = ["099720109477"] # Canonical
# }


#####################################################################
# Datalake - S3 Buckets and Event Notifications                     #
#####################################################################

##### BEGIN REMOVE #####
resource "aws_s3_bucket" "old_datalabs_lambda_code_bucket" {
    bucket = var.old_lambda_code_bucket

    lifecycle {
        prevent_destroy = true
    }

    tags = merge(local.tags, {Name = "Data Labs Lambda Code Bucket"})
}


resource "aws_s3_bucket" "datalabs_lambda_code_bucket" {
    bucket = var.lambda_code_bucket

    lifecycle {
        prevent_destroy = true
    }

    versioning {
        enabled = true
    }

    tags = merge(local.tags, {Name = "Data Labs Lambda Code Bucket"})
}


resource "aws_s3_bucket_public_access_block" "datalabs_lambda_code_bucket_public_access_block" {
    bucket = var.lambda_code_bucket

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

    depends_on = [aws_s3_bucket.datalabs_lambda_code_bucket]
}
##### END REMOVE #####

module "s3_ingested_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-datalake-ingested-data-${var.region}"

  lifecycle_rule = [
    {
      enabled = true

      transition = [
        {
          days          = 90
          storage_class = "STANDARD_IA"
          },
          {
          days          = 365
          storage_class = "GLACIER"
        }
      ]

    }
  ]

  app_name                          = lower(var.project)
  app_environment                   = var.environment

  tag_name                          = "${var.project}-${var.environment}-s3-ingested-data"
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


resource "aws_s3_bucket_notification" "sns_ingested_data" {
    bucket = module.s3_ingested_data.bucket_id
    topic {
        topic_arn           = module.sns_ingested_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


module "s3_processed_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-datalake-processed-data-${var.region}"

  lifecycle_rule = [
    {
      enabled = true

      transition = [
        {
          days          = 90
          storage_class = "STANDARD_IA"
          },
          {
          days          = 365
          storage_class = "GLACIER"
        }
      ]


    }
  ]

  app_name                          = lower(var.project)
  app_environment                   = var.environment

  tag_name                          = "${var.project}-${var.environment}-s3-processed-data"
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


resource "aws_s3_bucket_notification" "sns_processed_data" {
    bucket = module.s3_processed_data.bucket_id
    topic {
        topic_arn           = module.sns_processed_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


module "lambda_code_bucket" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-${lower(var.project)}-lambda-code-${var.region}"

  app_name                          = lower(var.project)
  app_environment                   = var.environment

  tag_name                          = "${var.project}-${var.environment}-s3-lambda-code"
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


#####################################################################
# Datalake - SNS Topics                                             #
#####################################################################

module "sns_ingested_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = "${var.ingested_data_topic_name}-${var.environment}"
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_ingested_data.bucket_id
  }

  name = "${var.ingested_data_topic_name}-${var.environment}"
  topic_display_name    = "${var.ingested_data_topic_name}-${var.environment}"
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                          = "${var.project}-${var.environment}-sns-ingested-topic"
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


module "sns_processed_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = "${var.processed_data_topic_name}-${var.environment}"
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_processed_data.bucket_id
  }

  name = "${var.processed_data_topic_name}-${var.environment}"
  topic_display_name    = "${var.processed_data_topic_name}-${var.environment}"
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                         = "${var.project}-${var.environment}-sns-processed-data"
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


#####################################################################
# Datalake - ECS Cluster, Service, and Task Definitions             #
#####################################################################

resource "aws_ecr_repository" "datanow" {
    name = "datanow"

    tags = merge(local.tags, {Name = "Data Labs Data Lake DataNow Container Repository"})
}


module "datalake_ecs_cluster" {
    source                            = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-fargate.git?ref=2.0.0"
    app_name                          =  lower(var.project)
    app_environment                   = var.environment

    tag_name                          = "${var.project}-cluster"
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


resource "aws_ecs_service" "datanow" {
    name                                = "DataNow"
    task_definition                     = module.datanow_task_definition.aws_ecs_task_definition_td_arn
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
            module.datanow_sg.security_group_id
        ]

        subnets             = [
            aws_subnet.datalake_public1.id,
            aws_subnet.datalake_public2.id
        ]
    }

    load_balancer {
        target_group_arn    = aws_lb_target_group.datanow.arn
        container_name      = "datanow"
        container_port      = "9047"
    }


    tags = merge(local.tags, {Name = "Data Labs Data Lake DataNow Service"})

    depends_on = [
        module.datanow_task_definition,
        aws_lb_target_group.datanow
    ]
}
# module "datanow_service" {
#     source                              = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-fargate-service.git?ref=2.0.0"
#     app_name                            = "DataNow"
#     container_name                      = "DataNow"  # The module should be using just app_name
#     resource_prefix                     = "${var.project}"
#     ecs_cluster_id                      = module.datalake_ecs_cluster.ecs_cluster_id
#     ecs_task_definition_arn             = module.datanow_task_definition.aws_ecs_task_definition_td_arn
#     task_count                          = 1
#     enable_autoscaling                  = true
#     create_discovery_record             = false  # Service Discovery is not currently implemented anyway
#     health_check_grace_period_seconds   = 0
#     ecs_security_groups                 = [module.datanow_sg.security_group_id]
#     alb_subnets_private                 = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
#
#     load_balancers                      = [
#         {
#             target_group_arn  = aws_lb_target_group.datanow.arn
#             container_name    = "datanow"
#             container_port    = "9047"
#         }
#     ]
#
#     sd_record_name                      = "DataNow"  # Service Discovery is not currently implemented, but this has no default
#
#     tag_name                            = "${var.project} DataNow Service"
#     tag_environment                   = var.environment
#     tag_contact                       = local.contact
#     tag_budgetcode                    = local.budget_code
#     tag_owner                         = local.owner
#     tag_projectname                   = local.project
#     tag_systemtier                    = local.tier
#     tag_drtier                        = local.tier
#     tag_dataclassification            = local.na
#     tag_notes                         = local.na
#     tag_eol                           = local.na
#     tag_maintwindow                   = local.na
#     tags = {
#         Group                               = local.group
#         Department                          = local.department
#     }
# }


module "datanow_task_definition" {
    source                          = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-ecs-fargate-task-definition.git?ref=2.0.0"
    task_name                       = "datanow"
    environment_name                = var.environment
    execution_role_arn              = aws_iam_role.datanow_execution.arn
    task_role_arn                   = aws_iam_role.datanow_task.arn
    container_cpu                   = 1024
    container_memory                = 8192

    container_definition_vars       = {
        account_id  = data.aws_caller_identity.account.account_id,
        region      = var.region
        image       = var.datanow_image
        tag         = var.datanow_version
    }

    volume = [
        {
            name                        = "DataNow"

            efs_volume_configuration    = [
                {
                    "file_system_id":       module.datanow_efs.filesystem_id
                    "root_directory":       "/"
                    "transit_encryption":   "ENABLED"

                    "authorization_config": {
                        "access_point_id":  module.datanow_efs.access_point_id
                        "iam":              "ENABLED"
                    }
                }
            ]
        }
    ]

    tag_name                        = "${var.project} DataNow Task"
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


resource "aws_alb" "datanow" {
    name               = "DataNow"
    internal           = false  # Internet-facing. Requires an Internet Gateway
    load_balancer_type = "application"

    subnets = [
        aws_subnet.datalake_public1.id,
        aws_subnet.datalake_public2.id
    ]

    security_groups = [
        module.datanow_sg.security_group_id,
    ]

    tags = merge(local.tags, {Name = "Data Lake DataNow Load Balancer"})

    depends_on = [aws_internet_gateway.datalake]
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


data "aws_acm_certificate" "amaaws" {
    domain = "*.amaaws.org"
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
}


module "datanow_sg" {
    source = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-security-group.git?ref=1.0.0"

    name        = "${lower(var.project)}-${var.environment}-datanow"
    description = "Security group for Datanow"
    vpc_id      = aws_vpc.datalake.id

    ingress_with_cidr_blocks = [
        {
            description = "HTTP Client"
            from_port   = "9047"
            to_port     = "9047"
            protocol    = "tcp"
            cidr_blocks = "0.0.0.0/0"
        },
        {
            description = "HTTP"
            from_port   = "80"
            to_port     = "80"
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
            description = "ODBC/JDBC Client"
            from_port   = "31010"
            to_port     = "31010"
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

    tags = merge(local.tags, {Name = "Data Lake DataNow Security Group"})
}


resource "aws_cloudwatch_log_group" "datanow" {
    name = "/ecs/datanow"

    tags = merge(local.tags, {Name = "Data Lake DataNow Log Group"})
}


resource "aws_iam_role" "datanow_task" {
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


resource "aws_iam_policy" "ecs_task_execution" {
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
            # "Condition": {
            #     "StringEquals": {
            #         "aws:sourceVpce": "${aws_vpc_endpoint.ecr.id}"
            #     }
            # }

resource "aws_iam_role_policy_attachment" "datanow_execution" {
    role        = aws_iam_role.datanow_execution.name
    policy_arn  = aws_iam_policy.ecs_task_execution.arn
}


# resource "aws_vpc_endpoint" "ecr_api" {
#     vpc_id              = aws_vpc.datalake.id
#     service_name        = "com.amazonaws.${var.region}.ecr.api"
#     vpc_endpoint_type   = "Interface"
#     private_dns_enabled = true
#
#     security_group_ids = [
#         module.datanow_sg.security_group_id
#     ]
#
#     subnet_ids          = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
#
#     tags = merge(local.tags, {Name = "Data Lake ECR API VPC Endpoint"})
# }
#
# resource "aws_vpc_endpoint" "ecr" {
#     vpc_id              = aws_vpc.datalake.id
#     service_name        = "com.amazonaws.${var.region}.ecr.dkr"
#     vpc_endpoint_type   = "Interface"
#     private_dns_enabled = true
#
#     security_group_ids = [
#         module.datanow_sg.security_group_id
#     ]
#
#     subnet_ids          = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
#
#     tags = merge(local.tags, {Name = "Data Lake ECR VPC Endpoint"})
# }
#
# resource "aws_vpc_endpoint" "logs" {
#     vpc_id              = aws_vpc.datalake.id
#     service_name        = "com.amazonaws.${var.region}.logs"
#     vpc_endpoint_type   = "Interface"
#     private_dns_enabled = true
#
#     security_group_ids = [
#         module.datanow_sg.security_group_id
#     ]
#
#     subnet_ids          = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
#
#     tags = merge(local.tags, {Name = "Data Lake Logs VPC Endpoint"})
# }
#
# resource "aws_vpc_endpoint" "s3" {
#     vpc_id              = aws_vpc.datalake.id
#     service_name        = "com.amazonaws.${var.region}.s3"
#     vpc_endpoint_type   = "Gateway"
#
#     tags = merge(local.tags, {Name = "Data Lake S3 VPC Endpoint"})
# }


#####################################################################
# Datalake - EFS Volume                                             #
#####################################################################

module "datanow_efs" {
    source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-efs.git?ref=2.0.0"
    performance_mode = "generalPurpose"
    transition_to_ia = "AFTER_14_DAYS"
    posix_user_gid   = 999
    posix_user_uid   = 999
    path_permissions = 755
    access_point_path = "/dremio"
    app_name                         = lower(var.project)
    app_environment                  = var.environment
    subnet_ids                       = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
    security_groups                  = [module.datanow_sg.security_group_id]

    tag_name                         = "${var.project}-${var.environment}-datanow-efs"
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


#####################################################################
# Datalake - Neptune Cluster                                        #
#####################################################################

# resource "aws_security_group" "lineage" {
#     name        = "Data Lake Lineage"
#     description = "Allow inbound traffic to Neptune"
#     vpc_id      = aws_vpc.datalake.id
#
#     ingress {
#         description = "Gremlin"
#         from_port   = 8182
#         to_port     = 8182
#         protocol    = "tcp"
#         # cidr_blocks = [aws_vpc.development.cidr_block]
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     egress {
#         from_port   = 0
#         to_port     = 0
#         protocol    = "-1"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     tags = merge(local.tags, {Name = "Data Lake Lineage SG"})
# }
#
#
# resource "aws_subnet" "lineage_frontend" {
#     vpc_id            = aws_vpc.datalake.id
#     cidr_block        = "172.31.0.0/24"
#     availability_zone = "us-east-1a"
#
#     tags = merge(local.tags, {Name = "Data Lake Lineage Fronend Subnet"})
# }
#
#
# resource "aws_route_table_association" "lineage_frontend" {
#     subnet_id      = aws_subnet.lineage_frontend.id
#     route_table_id = aws_vpc.datalake.default_route_table_id
# }
#
#
# resource "aws_subnet" "lineage_backend" {
#     vpc_id            = aws_vpc.datalake.id
#     cidr_block        = "172.31.1.0/24"
#     availability_zone = "us-east-1b"
#
#     tags = merge(local.tags, {Name = "Data Lake Lineage Backend Subnet"})
# }
#
#
# resource "aws_route_table_association" "lineage_backend" {
#     subnet_id      = aws_subnet.lineage_backend.id
#     route_table_id = aws_vpc.datalake.default_route_table_id
# }
#
#
# module "lineage_neptune_cluster" {
#     source  = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-neptune-cluster.git?ref=1.0.0"
#     app_name                          = lower(var.project)
#     instance_id                       = lower(var.project)
#     neptune_subnet_list     = [aws_subnet.lineage_frontend.id, aws_subnet.lineage_backend.id]
#     security_group_ids      = [aws_security_group.lineage.id]
#     environment                       = var.environment
#
#     tag_name                          = "${var.project}-${var.environment}-neptune-cluster"
#     tag_environment                   = var.environment
#     tag_contact                       = local.contact
#     tag_budgetcode                    = local.budget_code
#     tag_owner                         = local.owner
#     tag_projectname                   = local.project
#     tag_systemtier                    = local.tier
#     tag_drtier                        = local.tier
#     tag_dataclassification            = local.na
#     tag_notes                         = local.na
#     tag_eol                           = local.na
#     tag_maintwindow                   = local.na
#     tags = {
#         Group                               = local.group
#         Department                          = local.department
#     }
# }



#####################################################################
# Datalake - Lambda Functions
#####################################################################


module "datalabs_terraform_state" {
    source  = "../../Module/DataLake"
    project = "DataLake"
}


#####################################################################
# Web App Load Balancer
#####################################################################

module "webapp_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"
  name        = "${var.project}-${var.environment}-webapp-sg"
  description = "Security group for DataLabs web app load balancer"
  vpc_id      = aws_vpc.datalake.id

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "Web traffic"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = "7"
      to_port     = "7"
      protocol    = "icmp"
      description = "Ping"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = "-1"
      to_port     = "-1"
      protocol    = "-1"
      description = "outbound ports"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = merge(local.tags, {Name = "DataLabs web app load balancer security group"})
}

module "webapp_alb" {
  source                            = "app.terraform.io/AMA/alb/aws"
  version                           = "1.0.2"
  environment                       = var.environment
  name                              = "webapp"
  project                           = lower(var.project)
  description                       = "DataLabs Web APP Load Balancer"
  # vpc_id                            = aws_vpc.datalake.id
  vpc_id                            = aws_vpc.datalake.id
  # security_groups                   = [module.oneview_sg.security_group_id]
  security_groups                   = [module.webapp_sg.security_group_id]
  internal                          = true
  load_balancer_type                = "application"
  # subnet_ids                        = local.subnets
  subnet_ids                        = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
  enable_deletion_protection        = "false"
  target_type                       = "ip"
  target_group_port                 = 80
  target_group_protocol             = "HTTP"
  listener_port                     = 443
  listener_protocol                 = "HTTPS"
  ssl_policy                        = "ELBSecurityPolicy-2020-10"
  # certificate_arn                   = var.private_certificate_arn
  certificate_arn                   = data.aws_acm_certificate.amaaws.arn
  action                            = "forward"
  health_check_protocol             = "HTTP"
  health_check_port                 = 80
  health_check_interval             = 300
  health_check_path                 = "/"
  health_check_timeout              = "3"
  health_check_healthy_threshold    = "5"
  health_check_unhealthy_threshold  = "10"
  health_check_matcher              = "200"
  tag_name                          = "${var.project}-${var.environment}-webapp-alb"
  tag_environment                   = var.environment
  tag_contact                       = local.contact
  tag_budgetcode                    = local.budget_code
  tag_owner                         = local.owner
  tag_projectname                   = var.project
  tag_systemtier                    = "0"
  tag_drtier                        = "0"
  tag_dataclassification            = "N/A"
  tag_notes                         = "N/A"
  tag_eol                           = "N/A"
  tag_maintwindow                   = "N/A"
  tags = {}
}
