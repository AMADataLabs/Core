#####################################################################
# Security Group
#####################################################################

module "scheduler_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"
  name        = "${var.project}-${local.environment}-scheduler-sg"
  description = "Security group for Lambda VPC interfaces"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "User-service ports"
      cidr_blocks = "10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
    {
      from_port   = "5432"
      to_port     = "5432"
      protocol    = "tcp"
      description = "PostgreSQL ports"
      cidr_blocks = "10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
    {
      from_port   = "3306"
      to_port     = "3306"
      protocol    = "tcp"
      description = "MySQL ports"
      cidr_blocks = "10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
  ]
}


#####################################################################
# ECS Cluster
#####################################################################
# HADI ECS CUSTER
module "ecs_cluster" {
  source  = "app.terraform.io/AMA/fargate/aws"
  version = "2.0.0"
  app_name                          = lower(var.project)
  app_environment                   = local.environment
  tag_name                          = "${var.project}-${local.environment}-ecs-cluster"
  tag_environment                   = local.environment
  tag_contact                       = var.contact
  tag_budgetcode                    = var.budget_code
  tag_owner                         = var.owner
  tag_projectname                   = var.project
  tag_systemtier                    = "0"
  tag_drtier                        = "0"
  tag_dataclassification            = "N/A"
  tag_notes                         = "N/A"
  tag_eol                           = "N/A"
  tag_maintwindow                   = "N/A"
}

module "schedule_log_group" {
  source  = "app.terraform.io/AMA/cloudwatch-group/aws"
  version = "1.0.0"
  log_group_name          = "/ecs/scheduler/${local.environment}"
  environment                      = local.environment
  project                          = lower(var.project)
  tag_name                         = "${var.project}-${local.environment}-scheduler-log-group"
  tag_environment                   = local.environment
  tag_contact                       = var.contact
  tag_budgetcode                    = var.budget_code
  tag_owner                         = var.owner
  tag_projectname                   = var.project
  tag_systemtier                    = "0"
  tag_drtier                        = "0"
  tag_dataclassification            = "N/A"
  tag_notes                         = "N/A"
  tag_eol                           = "N/A"
  tag_maintwindow                   = "N/A"

}


#####################################################################
# ECS Execution Role
#####################################################################

data "aws_iam_policy_document" "ecs_task_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_role" {
    name                    = "${lower(var.project)}-${local.environment}-task-exe-role"
    assume_role_policy      = data.aws_iam_policy_document.ecs_task_role.json
    description             = "Allows ECS tasks to call AWS services on your behalf."

    tags                    = {
        Name                    = "ECS Task Role for OneView"
        Environment             = local.environment
        Contact                 = var.contact
        BudgetCode              = var.budget_code
        Owner                   = var.owner
        ProjectName             = var.project
        SystemTier              = "0"
        DRTier                  = "0"
        DataClassification      = "N/A"
        Notes                   = "N/A"
        OS                      = "N/A"
        EOL                     = "N/A"
        MaintenanceWindow       = "N/A"
        Group                   = "Health Solutions"
        Department              = "DataLabs"
    }
}


data "aws_iam_policy" "AmazonECSTaskExecutionRolePolicy" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = data.aws_iam_policy.AmazonECSTaskExecutionRolePolicy.arn
}


data "aws_iam_policy" "AmazonSSMReadOnlyAccess" {
  arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "ecs_task_ssm" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = data.aws_iam_policy.AmazonSSMReadOnlyAccess.arn
}


#####################################################################
# VPC Endpoints
#####################################################################

data "aws_vpc_endpoint" "api_gw_vpc_endpoint" {
  tags = {
    Name = "${local.environment}-execute-api_vpc_endpoint"
  }

  vpc_id       = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
}

data "aws_network_interface" "apigw_endpoint_eni" {
  for_each = data.aws_vpc_endpoint.api_gw_vpc_endpoint.network_interface_ids
  id       = each.value
}


#####################################################################
# Scheduler DAG Plugin
#####################################################################


##### ECS Service, and Task Definitions - Scheduler #####
# HADI SAMPLE FOR FARGATE
module "scheduler_service" {
    source  = "app.terraform.io/AMA/fargate-service/aws"
    version = "2.0.0"
    app_name                            = "scheduler"
    container_name                      = "scheduler"  # The module should be using just app_name
    resource_prefix                     = lower(var.project)
    ecs_cluster_id                      = module.ecs_cluster.ecs_cluster_id
    ecs_task_definition_arn             = module.scheduler_task_definition.aws_ecs_task_definition_td_arn
    task_count                          = 0
    enable_autoscaling                  = false
    create_discovery_record             = false  # Service Discovery is not currently implemented anyway
    health_check_grace_period_seconds   = 0
    ecs_security_groups                 = [module.scheduler_sg.security_group_id]
    alb_subnets_private                 = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    # load_balancers                      = [
    #     {
    #         target_group_arn  = module.datanow_alb.aws_lb_target_group_arn
    #         container_name    = "datanow"
    #         container_port    = "9047"
    #     }
    # ]
    sd_record_name                    = "Scheduler"  # Service Discovery is not currently implemented, but this has no default
    tag_name                          = "${var.project}-${local.environment}-scheduler-ecs-service"
    tag_environment                   = local.environment
    tag_contact                       = var.contact
    tag_budgetcode                    = var.budget_code
    tag_owner                         = var.owner
    tag_projectname                   = var.project
    tag_systemtier                    = "0"
    tag_drtier                        = "0"
    tag_dataclassification            = "N/A"
    tag_notes                         = "N/A"
    tag_eol                           = "N/A"
    tag_maintwindow                   = "N/A"
    tags = {}
}

module "scheduler_task_definition" {
    source  = "app.terraform.io/AMA/ecs-fargate-task-definition/aws"
    version = "2.0.0"
    task_name                       = "scheduler"
    environment_name                = local.environment
    task_role_arn                   = "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role"
    execution_role_arn              = "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role"
    container_cpu                   = 1024
    container_memory                = 8192
    container_definition_vars       = {
        account     = local.ecr_account
        region      = var.region
        image       = local.scheduler_image
        tag         = var.scheduler_version
        environment = local.environment
    }
    # volume                          = [
    #     {
    #         name                        = "DataNow"
    #         efs_volume_configuration    = [
    #             {
    #                 "file_system_id":       module.efs_cluster.filesystem_id
    #                 "root_directory":       "/"
    #                 "transit_encryption":   "ENABLED"
    #                 "authorization_config": {
    #                     "access_point_id":  module.efs_cluster.access_point_id
    #                     "iam":              "ENABLED"
    #                 }
    #             }
    #         ]
    #     }
    # ]
    tag_name                         = "${var.project}-${local.environment}-scheduler-td"
    tag_environment                   = local.environment
    tag_contact                       = var.contact
    tag_budgetcode                    = var.budget_code
    tag_owner                         = var.owner
    tag_projectname                   = var.project
    tag_systemtier                    = "0"
    tag_drtier                        = "0"
    tag_dataclassification            = "N/A"
    tag_notes                         = "N/A"
    tag_eol                           = "N/A"
    tag_maintwindow                   = "N/A"
    tags = {}
}

#####################################################################
# AWS Batch
#####################################################################

##### aws_iam_role - Scheduler #####
resource "aws_iam_role" "aws_batch_service_role" {
  name = "aws_batch_service_role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_role.json

  tags = {
    Name = "${var.project}-${local.environment}-aws-batch-service-role"
    Environment             = local.environment
    Contact                 = var.contact
    BudgetCode              = var.budget_code
    Owner                   = var.owner
    ProjectName             = var.project
    SystemTier              = "0"
    DRTier                  = "0"
    DataClassification      = "N/A"
    Notes                   = "N/A"
    OS                      = "N/A"
    EOL                     = "N/A"
    MaintenanceWindow       = "N/A"
    Group                   = "Health Solutions"
    Department              = "DataLabs"
  }
}


##### aws_iam_role_policy_attachment - Scheduler #####
resource "aws_iam_role_policy_attachment" "aws_batch_service_role" {
  role       = aws_iam_role.aws_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role_policy_attachment" "secret_manager_read_write" {
  role       = aws_iam_role.aws_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

##### batch_compute_environment - Scheduler #####
resource "aws_batch_compute_environment" "ecs_scheduler_env" {
  compute_environment_name = "ecs-scheduler-env"

  compute_resources {
    max_vcpus = 2

    security_group_ids = [
      module.scheduler_sg.security_group_id
    ]

    #NOTE: HADI, are you sure? ask Peter
    subnets = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    # subnets = ["subnet-0a508711165923924"]
    # subnets = ["arn:aws:ec2:us-east-1:644454719059:subnet/subnet-0a508711165923924"]

    type = "FARGATE"
  }

  service_role = aws_iam_role.aws_batch_service_role.arn
  # service_role = "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role"
  type         = "MANAGED"
  depends_on   = [aws_iam_role_policy_attachment.aws_batch_service_role]
  tags = {
    Name = "${var.project}-${local.environment}-ecs-scheduler-env"
    Environment             = local.environment
    Contact                 = var.contact
    BudgetCode              = var.budget_code
    Owner                   = var.owner
    ProjectName             = var.project
    SystemTier              = "0"
    DRTier                  = "0"
    DataClassification      = "N/A"
    Notes                   = "N/A"
    OS                      = "N/A"
    EOL                     = "N/A"
    MaintenanceWindow       = "N/A"
    Group                   = "Health Solutions"
    Department              = "DataLabs"
  }
}

##### batch_job_queue - Scheduler #####
resource "aws_batch_job_queue" "ecs_scheduler_job_queue" {
  name     = "ecs-scheduler-job-queue"
  state    = "ENABLED"
  priority = 1
  compute_environments = [
    aws_batch_compute_environment.ecs_scheduler_env.arn,
  ]

  tags = {
    Name = "${var.project}-${local.environment}-ecs-scheduler-job-queue"
    Environment             = local.environment
    Contact                 = var.contact
    BudgetCode              = var.budget_code
    Owner                   = var.owner
    ProjectName             = var.project
    SystemTier              = "0"
    DRTier                  = "0"
    DataClassification      = "N/A"
    Notes                   = "N/A"
    OS                      = "N/A"
    EOL                     = "N/A"
    MaintenanceWindow       = "N/A"
    Group                   = "Health Solutions"
    Department              = "DataLabs"
  }
}

##### batch_job_definition - Scheduler #####
resource "aws_batch_job_definition" "ecs-scheduler-job-definition" {
  name = "ecs-scheduler-job-definition"
  type = "container"
  platform_capabilities = [
    "FARGATE",
  ]

  container_properties = <<CONTAINER_PROPERTIES
{
  "command": ["python","task.py","'{\"dag\": \"DAG_SCHEDULER\", \"type\": \"DAG\", \"task\": \"_\", \"execution_time\": \"2020-11-10 21:30:00.000\"}'"],
  "image": "644454719059.dkr.ecr.us-east-1.amazonaws.com/datalake-sbx",
  "fargatePlatformConfiguration": {
    "platformVersion": "1.3.0"
  },
  "resourceRequirements": [
    {"type": "VCPU", "value": "1"},
    {"type": "MEMORY", "value": "2048"}
  ],
  "executionRoleArn": "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role",
  "jobRoleArn": "${aws_iam_role.aws_batch_service_role.arn}",
  "environment": [ 
         { 
            "name": "ECS_AVAILABLE_LOGGING_DRIVERS",
            "value": "awslogs"
         }
      ]
}
CONTAINER_PROPERTIES
  # "jobRoleArn": "${aws_iam_role.ecs_task_role.arn}"

#   container_properties = <<CONTAINER_PROPERTIES
# {
#   "command": ["echo", "test"],
#   "image": "busybox",
#   "fargatePlatformConfiguration": {
#     "platformVersion": "LATEST"
#   },
#   "resourceRequirements": [
#     {"type": "VCPU", "value": "1"},
#     {"type": "MEMORY", "value": "2048"}
#   ],
#   "executionRoleArn": "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role"
# }
# CONTAINER_PROPERTIES
}