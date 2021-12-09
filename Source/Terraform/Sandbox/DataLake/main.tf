#Get the running execution context
data "aws_caller_identity" "account" {}

#####################################################################
# Datalake - Keys           #
#####################################################################

resource "aws_kms_key" "key" {
    customer_master_key_spec = "SYMMETRIC_DEFAULT"
    description              = "DynamoDB Encryption"
    enable_key_rotation      = true
    is_enabled               = true
    key_usage                = "ENCRYPT_DECRYPT"
}

resource "aws_kms_alias" "key_alias" {
    name           = "alias/dl-${local.environment}-dynamodb-us-east-1"
    target_key_id  = aws_kms_key.key.id
}

#####################################################################
# Datalake - Add application specific modules, data, locals, etc....           #
#####################################################################

resource "random_password" "datanow_password" {
  length = 16
  special = true
  override_special = "_%"
  # Reference with random_password.datanow_password.result
}


#####################################################################
# Datalake - S3 Buckets and Event Notifications                     #
#####################################################################

module "s3_ingested" {
    source  = "app.terraform.io/AMA/s3/aws"
    version = "2.0.0"

  enable_versioning = true
  bucket_name = "ama-${local.environment}-datalake-ingest-${var.region}"

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
  app_environment                   = local.environment

  tag_name                          = "${var.project}-${local.environment}-s3-ingested-data"
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
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}

#s3 event notifications here
resource "aws_s3_bucket_notification" "ingested_data_sns_notification" {
    bucket = module.s3_ingested.bucket_id
    topic {
        topic_arn           = module.sns_ingested_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


module "s3_processed" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name = "ama-${local.environment}-datalake-process-${var.region}"

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
  app_environment                   = local.environment

  tag_name                          = "${var.project}-${local.environment}-s3-processed-data"
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
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}

module "s3_scheduler" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name = "ama-${local.environment}-datalake-scheduler-${var.region}"

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
  app_environment                   = local.environment

  tag_name                          = "${var.project}-${local.environment}-s3-scheduler-data"
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
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}

module "s3_webapp_content" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name = "ama-${local.environment}-datalake-webapp-content-${var.region}"

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
  app_environment                   = local.environment
  tag_name                          = "${var.project}-${local.environment}-s3-webapp-content-bucket"
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
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}

# S3 event notifications here
resource "aws_s3_bucket_notification" "processed_data_sns_notification" {
    bucket = module.s3_processed.bucket_id
    topic {
        topic_arn           = module.sns_processed_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}

resource "aws_s3_bucket_notification" "sns_scheduler" {
    bucket = module.s3_scheduler.bucket_id
    topic {
        topic_arn           = module.sns_scheduler_topic.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


module "s3_lambda" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name = "ama-${local.environment}-${lower(var.project)}-lambda-code-${var.region}"

  app_name                          = lower(var.project)
  app_environment                   = local.environment

  tag_name                          = "${var.project}-${local.environment}-s3-lambda-code"
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
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


#####################################################################
# Lambda
#####################################################################

module "lambda_dag_processor" {
    source  = "app.terraform.io/AMA/lambda/aws"
    version = "2.0.0"
    function_name       = local.lambda_names.dag_processor
    lambda_name         = local.lambda_names.dag_processor
    s3_lambda_bucket    = local.s3_lambda_bucket
    s3_lambda_key       = "Scheduler.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.lambda_memory_size
    timeout             = var.lambda_timeout

    vpc_config = {
        subnet_ids              = data.terraform_remote_state.infrastructure.outputs.subnet_ids
        security_group_ids      = [module.datanow_sg.security_group_id]
    }

    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = true
    #Bogus ARN Used to satisfy module requirement
    api_arn                   = "arn:aws-partition:service:${var.region}:${data.aws_caller_identity.account.account_id}:resource-id"

    environment_variables = {
        variables = {
          TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.ProcessorTaskWrapper"
          TASK_CLASS              = "datalabs.etl.dag.process.DAGProcessorTask"
          DYNAMODB_CONFIG_TABLE   = aws_dynamodb_table.configuration.id
        }
    }

    tag_name                          = local.lambda_names.dag_processor
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

resource "aws_lambda_permission" "lambda_dag_processor" {
     statement_id    = "AllowSNSInvoke-DAG"
     action          = "lambda:InvokeFunction"
     function_name   = module.lambda_dag_processor.function_name
     principal       = "sns.amazonaws.com"
     source_arn      = module.sns_dag_topic.topic_arn
}

resource "aws_lambda_permission" "lambda_dag_processor_scheduler" {
     statement_id    = "AllowSNSInvoke-Scheduler"
     action          = "lambda:InvokeFunction"
     function_name   = module.lambda_dag_processor.function_name
     principal       = "sns.amazonaws.com"
     source_arn      = module.sns_scheduler_topic.topic_arn
}


module "lambda_task_processor" {
    source  = "app.terraform.io/AMA/lambda/aws"
    version = "2.0.0"
    function_name       = local.lambda_names.task_processor
    lambda_name         = local.lambda_names.task_processor
    s3_lambda_bucket    = local.s3_lambda_bucket
    s3_lambda_key       = "Scheduler.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.lambda_memory_size
    timeout             = var.lambda_timeout

    vpc_config = {
        subnet_ids              = data.terraform_remote_state.infrastructure.outputs.subnet_ids
        security_group_ids      = [module.datanow_sg.security_group_id]
    }

    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = true
    #Bogus ARN Used to satisfy module requirement
    api_arn                   = "arn:aws-partition:service:${var.region}:${data.aws_caller_identity.account.account_id}:resource-id"

    environment_variables = {
        variables = {
          TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.ProcessorTaskWrapper"
          TASK_CLASS              = "datalabs.etl.dag.process.TaskProcessorTask"
          DYNAMODB_CONFIG_TABLE   = aws_dynamodb_table.configuration.id
        }
    }

    tag_name                          = local.lambda_names.task_processor
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


resource "aws_lambda_permission" "lambda_task_processor" {
    statement_id    = "AllowSNSInvoke"
    action          = "lambda:InvokeFunction"
    function_name   = module.lambda_task_processor.function_name
    principal       = "sns.amazonaws.com"
    source_arn      = module.sns_task_topic.topic_arn
}


module "lambda_scheduler" {
    source  = "app.terraform.io/AMA/lambda/aws"
    version = "2.0.0"
    function_name       = local.lambda_names.scheduler
    lambda_name         = local.lambda_names.scheduler
    s3_lambda_bucket    = local.s3_lambda_bucket
    s3_lambda_key       = "Scheduler.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.lambda_memory_size
    timeout             = var.lambda_timeout

    vpc_config = {
      subnet_ids              = data.terraform_remote_state.infrastructure.outputs.subnet_ids
      security_group_ids      = [module.datanow_sg.security_group_id]
    }

    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = true
    api_arn                   = "arn:aws-partition:service:${var.region}:${data.aws_caller_identity.account.account_id}:resource-id"

    environment_variables = {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.DAGTaskWrapper"
            TASK_RESOLVER_CLASS     = "datalabs.etl.dag.resolve.TaskResolver"
            DYNAMODB_CONFIG_TABLE   = aws_dynamodb_table.configuration.id
            DAG_CLASS               = "datalabs.etl.dag.schedule.dag.DAGSchedulerDAG"
        }
    }

    tag_name                = local.lambda_names.scheduler
    tag_environment         = local.tags["Environment"]
    tag_contact             = local.tags["Contact"]
    tag_systemtier          = local.tags["SystemTier"]
    tag_drtier              = local.tags["DRTier"]
    tag_dataclassification  = local.tags["DataClassification"]
    tag_budgetcode          = local.tags["BudgetCode"]
    tag_owner               = local.tags["Owner"]
    tag_projectname         = var.project
    tag_notes               = ""
    tag_eol                 = local.tags["EOL"]
    tag_maintwindow         = local.tags["MaintenanceWindow"]
}


#####################################################################
# Datalake - SNS Topics                                             #
#####################################################################

module "sns_ingested_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = local.topic_names.ingested_data
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_ingested.bucket_id
  }

  name = local.topic_names.ingested_data
  topic_display_name    = local.topic_names.ingested_data
  app_name              = lower(var.project)
  app_environment       = local.environment

  tag_name                          = "${var.project}-${local.environment}-sns-ingested-topic"
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
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


module "sns_processed_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = local.topic_names.processed_data
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_processed.bucket_id
  }

  name                  = local.topic_names.processed_data
  topic_display_name    = local.topic_names.processed_data
  app_name              = lower(var.project)
  app_environment       = local.environment

  tag_name                          = "${local.topic_names.processed_data}-topic"
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
    app_environment                   = local.environment

    tag_name                          = "${upper(var.project)}-${local.environment}-ECS-CLUSTER"
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
            aws_subnet.datalake_private1.id,
            aws_subnet.datalake_private2.id
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
#     tag_environment                   = local.environment
#     tag_contact                       = var.contact
#     tag_budgetcode                    = var.budget_code
#     tag_owner                         = var.owner
#     tag_projectname                   = var.project
#     tag_systemtier                    = "0"
#     tag_drtier                        = "0"
#     tag_dataclassification            = "N/A"
#     tag_notes                         = "N/A"
#     tag_eol                           = "N/A"
#     tag_maintwindow                   = "N/A"
#     tags = {
#         Group                               = local.group
#         Department                          = local.department
#     }
# }


module "datanow_task_definition" {
    source                          = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-ecs-fargate-task-definition.git?ref=2.0.0"
    task_name                       = "datanow"
    environment_name                = local.environment
    execution_role_arn              = aws_iam_role.datanow_execution.arn
    task_role_arn                   = aws_iam_role.datanow_task.arn
    container_cpu                   = 1024
    container_memory                = 8192

    container_definition_vars       = {
        account_id  = data.aws_caller_identity.account.account_id,
        region      = var.region
        image       = local.datanow_image
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

    name        = "${lower(var.project)}-${local.environment}-datanow"
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
    app_environment                  = local.environment
    subnet_ids                       = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
    security_groups                  = [module.datanow_sg.security_group_id]

    tag_name                         = "${var.project}-${local.environment}-datanow-efs"
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
#     environment                       = local.environment
#
#     tag_name                          = "${var.project}-${local.environment}-neptune-cluster"
#     tag_environment                   = local.environment
#     tag_contact                       = var.contact
#     tag_budgetcode                    = var.budget_code
#     tag_owner                         = var.owner
#     tag_projectname                   = var.project
#     tag_systemtier                    = "0"
#     tag_drtier                        = "0"
#     tag_dataclassification            = "N/A"
#     tag_notes                         = "N/A"
#     tag_eol                           = "N/A"
#     tag_maintwindow                   = "N/A"
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
  name        = "${var.project}-${local.environment}-webapp-sg"
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
  environment                       = local.environment
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
  tag_name                          = "${var.project}-${local.environment}-webapp-alb"
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
