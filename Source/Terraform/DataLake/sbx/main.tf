#####################################################################
# Storage (S3, Database)                                            #
#####################################################################


#####################################################################
# Lineage (Neptune)                                                 #
#####################################################################


#####################################################################
# Exploration (DataNow)                                            #
#####################################################################


#####################################################################
# DAG Scheduler(Lambda, SNS, DynamoDB)                              #
#####################################################################


#####################################################################
# DataLabs Webapp Load Balancer (ALB)                               #
#####################################################################


#####################################################################
# Datalake - Keys                                                   #
#####################################################################

resource "aws_kms_key" "key" {
  customer_master_key_spec = "SYMMETRIC_DEFAULT"
  description              = "DynamoDB Encryption"
  enable_key_rotation      = true
  is_enabled               = true
  key_usage                = "ENCRYPT_DECRYPT"
}

resource "aws_kms_alias" "key_alias" {
  name          = "alias/dl-${local.environment}-dynamodb-us-east-1"
  target_key_id = aws_kms_key.key.id
}

#####################################################################
# Datalake - Add application specific modules, data, locals, etc....#
#####################################################################

resource "random_password" "datanow_password" {
  length           = 16
  special          = true
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
  bucket_name       = "ama-${local.environment}-datalake-ingest-${local.region}"

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

  app_name        = lower(local.project)
  app_environment = local.environment

  tag_name               = "${local.project}-${local.environment}-s3-ingested-data"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

#s3 event notifications here
resource "aws_s3_bucket_notification" "ingested_data_sns_notification" {
  bucket = module.s3_ingested.bucket_id
  topic {
    topic_arn = module.sns_ingested.topic_arn
    events    = ["s3:ObjectCreated:*"]
  }
}


module "s3_processed" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name       = "ama-${local.environment}-datalake-process-${local.region}"

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

  app_name        = lower(local.project)
  app_environment = local.environment

  tag_name               = "${local.project}-${local.environment}-s3-processed-data"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module "s3_scheduler" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name       = "ama-${local.environment}-datalake-scheduler-${local.region}"

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

  app_name        = lower(local.project)
  app_environment = local.environment

  tag_name               = "${local.project}-${local.environment}-s3-scheduler-data"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module "s3_webapp_content" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name       = "ama-${local.environment}-datalake-webapp-content-${local.region}"

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

  app_name               = lower(local.project)
  app_environment        = local.environment
  tag_name               = "${local.project}-${local.environment}-s3-webapp-content"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

# S3 event notifications here
resource "aws_s3_bucket_notification" "processed_data_sns_notification" {
  bucket = module.s3_processed.bucket_id
  topic {
    topic_arn = module.sns_processed.topic_arn
    events    = ["s3:ObjectCreated:*"]
  }
}

resource "aws_s3_bucket_notification" "scheduler_data_sns_notification" {
  bucket = module.s3_scheduler.bucket_id
  topic {
    topic_arn = module.sns_scheduler.topic_arn
    events    = ["s3:ObjectCreated:*"]
  }
}

module "s3_lambda" {
  source  = "app.terraform.io/AMA/s3/aws"
  version = "2.0.0"

  enable_versioning = true
  bucket_name       = local.s3_lambda_bucket

  app_name        = lower(local.project)
  app_environment = local.environment

  tag_name               = local.s3_lambda_bucket
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}


#####################################################################
# Lambda
#####################################################################

module "lambda_dag_processor" {
  source           = "app.terraform.io/AMA/lambda/aws"
  version          = "2.0.0"
  function_name    = local.lambda_names.dag_processor
  lambda_name      = local.lambda_names.dag_processor
  s3_lambda_bucket = local.s3_lambda_bucket
  s3_lambda_key    = "Scheduler.zip"
  handler          = "awslambda.handler"
  runtime          = local.python_runtime
  create_alias     = false
  memory_size      = 1024
  timeout          = 5

  vpc_config = {
    subnet_ids         = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    security_group_ids = [module.datanow_alb_sg.security_group_id]
  }

  lambda_policy_vars = {
    account_id = local.account
    region     = local.region
    project    = local.project
  }

  create_lambda_permission = false
  #Bogus ARN Used to satisfy module requirement
  api_arn = "arn:aws-partition:service:${local.region}:${local.account}:resource-id"

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS    = "datalabs.etl.dag.awslambda.ProcessorTaskWrapper"
      TASK_CLASS            = "datalabs.etl.dag.process.DAGProcessorTask"
      DYNAMODB_CONFIG_TABLE = module.dynamodb_dag_configuration.dynamodb_table_id
    }
  }

  tag_name               = local.lambda_names.dag_processor
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}

resource "aws_lambda_permission" "lambda_dag_processor" {
  statement_id  = "AllowSNSInvoke-DAG"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_dag_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.sns_dag.topic_arn
}

resource "aws_lambda_permission" "lambda_dag_processor_scheduler" {
  statement_id  = "AllowSNSInvoke-Scheduler"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_dag_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.sns_scheduler.topic_arn
}


module "lambda_task_processor" {
  source           = "app.terraform.io/AMA/lambda/aws"
  version          = "2.0.0"
  function_name    = local.lambda_names.task_processor
  lambda_name      = local.lambda_names.task_processor
  s3_lambda_bucket = local.s3_lambda_bucket
  s3_lambda_key    = "Scheduler.zip"
  handler          = "awslambda.handler"
  runtime          = local.python_runtime
  create_alias     = false
  memory_size      = 1024
  timeout          = 5

  vpc_config = {
    subnet_ids         = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    security_group_ids = [module.datanow_alb_sg.security_group_id]
  }

  lambda_policy_vars = {
    account_id = local.account
    region     = local.region
    project    = local.project
  }

  create_lambda_permission = false
  #Bogus ARN Used to satisfy module requirement
  api_arn = "arn:aws-partition:service:${local.region}:${local.account}:resource-id"

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS    = "datalabs.etl.dag.awslambda.ProcessorTaskWrapper"
      TASK_CLASS            = "datalabs.etl.dag.process.TaskProcessorTask"
      DYNAMODB_CONFIG_TABLE = module.dynamodb_dag_configuration.dynamodb_table_id
    }
  }

  tag_name               = local.lambda_names.task_processor
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}


resource "aws_lambda_permission" "lambda_task_processor" {
  statement_id  = "AllowSNSInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_task_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = module.sns_task.topic_arn
}


module "lambda_scheduler" {
  source           = "app.terraform.io/AMA/lambda/aws"
  version          = "2.0.0"
  function_name    = local.lambda_names.scheduler
  lambda_name      = local.lambda_names.scheduler
  s3_lambda_bucket = local.s3_lambda_bucket
  s3_lambda_key    = "Scheduler.zip"
  handler          = "awslambda.handler"
  runtime          = local.python_runtime
  create_alias     = false
  memory_size      = 1024
  timeout          = 15

  vpc_config = {
    subnet_ids         = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    security_group_ids = [module.datanow_alb_sg.security_group_id]
  }

  lambda_policy_vars = {
    account_id = local.account
    region     = local.region
    project    = local.project
  }

  create_lambda_permission = false
  #Bogus ARN Used to satisfy module requirement
  api_arn = "arn:aws-partition:service:${local.region}:${local.account}:resource-id"

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS    = "datalabs.etl.dag.awslambda.DAGTaskWrapper"
      TASK_RESOLVER_CLASS   = "datalabs.etl.dag.resolve.TaskResolver"
      DYNAMODB_CONFIG_TABLE = module.dynamodb_dag_configuration.dynamodb_table_id
      DAG_CLASS             = "datalabs.etl.dag.schedule.dag.DAGSchedulerDAG"
    }
  }

  tag_name               = local.lambda_names.scheduler
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}


module "lambda_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "datalake-${local.environment}-lambda-sg"
  description = "Security group for DataLake Lambda functions"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "HTTPS"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
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

  tags = merge(local.tags, { Name = "${upper(local.project)}-${upper(local.environment)}-LAMBDA-SG" })
  # tag_name               = "${upper(local.project)}-${upper(local.environment)}-LAMBDA-SG"
  # tag_environment        = local.environment
  # tag_contact            = local.contact
  # tag_budgetcode         = local.budget_code
  # tag_owner              = local.owner
  # tag_projectname        = local.project
  # tag_systemtier         = "0"
  # tag_drtier             = "0"
  # tag_dataclassification = "N/A"
  # tag_notes              = "N/A"
  # tag_eol                = "N/A"
  # tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}


#####################################################################
# Datalake - SNS Topics and Subscriptions                           #
#####################################################################

module "sns_ingested" {
  source  = "app.terraform.io/AMA/sns/aws"
  version = "1.0.0"

  policy_template_vars = {
    topic_name     = local.topic_names.ingested_data
    region         = local.region
    account_id     = local.account
    s3_bucket_name = module.s3_ingested.bucket_id
  }

  name               = local.topic_names.ingested_data
  topic_display_name = local.topic_names.ingested_data
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = "${local.topic_names.ingested_data}-topic"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}


module "sns_processed" {
  source  = "app.terraform.io/AMA/sns/aws"
  version = "1.0.0"

  policy_template_vars = {
    topic_name     = local.topic_names.processed_data
    region         = local.region
    account_id     = local.account
    s3_bucket_name = module.s3_processed.bucket_id
  }

  name               = local.topic_names.processed_data
  topic_display_name = local.topic_names.processed_data
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = "${local.topic_names.processed_data}-topic"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}


module "sns_scheduler" {
  source  = "app.terraform.io/AMA/sns/aws"
  version = "1.0.0"

  policy_template_vars = {
    topic_name     = local.topic_names.scheduler
    region         = local.region
    account_id     = local.account
    s3_bucket_name = module.s3_scheduler.bucket_id
  }

  name               = local.topic_names.scheduler
  topic_display_name = local.topic_names.scheduler
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = "${local.topic_names.scheduler}-topic"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

resource "aws_sns_topic_subscription" "lambda_scheduler" {
  topic_arn = module.sns_scheduler.topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_dag_processor.function_arn
}


module "sns_dag" {
  source  = "app.terraform.io/AMA/sns/aws"
  version = "1.0.0"

  policy_template_vars = {
    topic_name     = local.topic_names.dag_processor
    region         = local.region
    account_id     = local.account
    s3_bucket_name = module.s3_scheduler.bucket_id
  }

  name               = local.topic_names.dag_processor
  topic_display_name = local.topic_names.dag_processor
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = "${local.topic_names.dag_processor}-topic"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

resource "aws_sns_topic_subscription" "lambda_dag_processor" {
  topic_arn = module.sns_dag.topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_dag_processor.function_arn
}


module "sns_task" {
  source  = "app.terraform.io/AMA/sns/aws"
  version = "1.0.0"

  policy_template_vars = {
    topic_name     = local.topic_names.task_processor
    region         = local.region
    account_id     = local.account
    s3_bucket_name = module.s3_scheduler.bucket_id
  }

  name               = local.topic_names.task_processor
  topic_display_name = local.topic_names.task_processor
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = "${local.topic_names.task_processor}-topic"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}


resource "aws_sns_topic_subscription" "lambda_task_processor" {
  topic_arn = module.sns_task.topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_task_processor.function_arn
}


#####################################################################
# ECS Cluster                                                       #
#####################################################################

module "ecs_cluster" {
  source          = "app.terraform.io/AMA/fargate/aws"
  version         = "2.0.0"

  app_name        = lower(local.project)
  app_environment = local.environment

  tag_name               = "${local.project}-${local.environment}-ecs-cluster"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}


#####################################################################
# DataLake - DataNow                                                #
#####################################################################

module "datanow_service" {
  source                            = "app.terraform.io/AMA/fargate-service/aws"
  version                           = "2.0.0"
  app_name                          = "datanow"
  container_name                    = "datanow" # The module should be using just app_name
  resource_prefix                   = lower(local.project)
  ecs_cluster_id                    = module.ecs_cluster.ecs_cluster_id
  ecs_task_definition_arn           = module.datanow_task_definition.aws_ecs_task_definition_td_arn
  task_count                        = 1
  enable_autoscaling                = false
  create_discovery_record           = false # Service Discovery is not currently implemented anyway
  health_check_grace_period_seconds = 0
  ecs_security_groups               = [module.datanow_ecs_service_sg.security_group_id]
  alb_subnets_private               = data.terraform_remote_state.infrastructure.outputs.subnet_ids
  load_balancers = [
    {
      target_group_arn = module.datanow-alb.aws_lb_target_group_arn
      container_name   = "datanow"
      container_port   = "9047"
    }
  ]
  sd_record_name         = "DataNow" # Service Discovery is not currently implemented, but this has no default
  tag_name               = "${local.project}-${local.environment}-datanow-ecs-service"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module "datanow-alb" {
  source                           = "app.terraform.io/AMA/alb/aws"
  version                          = "1.0.2"
  environment                      = local.environment
  name                             = "datanow"
  project                          = lower(local.project)
  description                      = "UI to access the datalake data"
  vpc_id                           = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
  security_groups                  = [module.datanow_alb_sg.security_group_id]
  internal                         = true
  load_balancer_type               = "application"
  subnet_ids                       = data.terraform_remote_state.infrastructure.outputs.subnet_ids
  enable_deletion_protection       = "false"
  target_type                      = "ip"
  target_group_port                = 9047
  target_group_protocol            = "HTTP"
  listener_port                    = 443
  listener_protocol                = "HTTPS"
  ssl_policy                       = "ELBSecurityPolicy-2020-10"
  certificate_arn                  = var.public_certificate_arn
  action                           = "forward"
  health_check_protocol            = "HTTP"
  health_check_port                = 9047
  health_check_interval            = 300
  health_check_path                = "/apiv2/server_status"
  health_check_timeout             = "3"
  health_check_healthy_threshold   = "5"
  health_check_unhealthy_threshold = "10"
  health_check_matcher             = "200"
  tag_name                         = "${local.project}-${local.environment}-datanow-alb"
  tag_environment                  = local.environment
  tag_contact                      = local.contact
  tag_budgetcode                   = local.budget_code
  tag_owner                        = local.owner
  tag_projectname                  = local.project
  tag_systemtier                   = "0"
  tag_drtier                       = "0"
  tag_dataclassification           = "N/A"
  tag_notes                        = "N/A"
  tag_eol                          = "N/A"
  tag_maintwindow                  = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module "datanow_task_definition" {
  source             = "app.terraform.io/AMA/ecs-fargate-task-definition/aws"
  version            = "2.0.0"
  task_name          = "datanow"
  environment_name   = local.environment
  task_role_arn      = "arn:aws:iam::${local.account}:role/dl-${local.environment}-task-exe-role"
  execution_role_arn = "arn:aws:iam::${local.account}:role/dl-${local.environment}-task-exe-role"
  container_cpu      = 1024
  container_memory   = 8192
  container_definition_vars = {
    account_id  = local.account,
    region      = local.region
    image       = local.datanow_image
    tag         = var.datanow_version
    environment = local.environment
  }
  volume = [
    {
      name = "DataNow"
      efs_volume_configuration = [
        {
          "file_system_id" : module.efs_cluster.filesystem_id
          "root_directory" : "/"
          "transit_encryption" : "ENABLED"
          "authorization_config" : {
            "access_point_id" : module.efs_cluster.access_point_id
            "iam" : "ENABLED"
          }
        }
      ]
    }
  ]
  tag_name               = "${local.project}-${local.environment}-datanow-td"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module efs_cluster {
  source                 = "app.terraform.io/AMA/efs/aws"
  version                = "2.0.0"
  performance_mode       = "generalPurpose"
  transition_to_ia       = "AFTER_14_DAYS"
  posix_user_gid         = 999
  posix_user_uid         = 999
  path_permissions       = 755
  access_point_path      = "/dremio"
  app_name               = lower(local.project)
  app_environment        = local.environment
  subnet_ids             = data.terraform_remote_state.infrastructure.outputs.subnet_ids
  security_groups        = [module.efs_sg.security_group_id]

  tag_name               = "${local.project}-${local.environment}-datanow-efs-cluster"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module "datanow_ecs_service_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "datalake-${local.environment}-datanow-ecs-service-sg"
  description = "Security group for Fargate (ECS) service interfaces"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "9047"
      to_port     = "9047"
      protocol    = "tcp"
      description = "Dremio UI (HTTPS)"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
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

  tags = merge(local.tags, { Name = "${upper(local.project)}-${upper(local.environment)}-DATANOW-ECS-SG" })
  # tag_name               = "${upper(local.project)}-${upper(local.environment)}-DATANOW-ECS-SG"
  # tag_environment        = local.environment
  # tag_contact            = local.contact
  # tag_budgetcode         = local.budget_code
  # tag_owner              = local.owner
  # tag_projectname        = local.project
  # tag_systemtier         = "0"
  # tag_drtier             = "0"
  # tag_dataclassification = "N/A"
  # tag_notes              = "N/A"
  # tag_eol                = "N/A"
  # tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}

module "datanow_alb_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "datalake-${local.environment}-datanow-alb-sg"
  description = "Security group for DataNow Load Balancer"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "HTTPS"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
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

  tags = merge(local.tags, { Name = "${upper(local.project)}-${upper(local.environment)}-DATANOW-ALB-SG" })
  # tag_name               = "${upper(local.project)}-${upper(local.environment)}-DATANOW-ALB-SG"
  # tag_environment        = local.environment
  # tag_contact            = local.contact
  # tag_budgetcode         = local.budget_code
  # tag_owner              = local.owner
  # tag_projectname        = local.project
  # tag_systemtier         = "0"
  # tag_drtier             = "0"
  # tag_dataclassification = "N/A"
  # tag_notes              = "N/A"
  # tag_eol                = "N/A"
  # tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}

module "efs_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "datalake-${local.environment}-datanow-efs-sg"
  description = "Security group for the Datanow EFS cluster"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "2049"
      to_port     = "2049"
      protocol    = "tcp"
      description = "EFS (NFS)"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
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

  tags = merge(local.tags, { Name = "${upper(local.project)}-${upper(local.environment)}-EFS-SG" })
  # tag_name               = "${upper(local.project)}-${upper(local.environment)}-EFS-SG"
  # tag_environment        = local.environment
  # tag_contact            = local.contact
  # tag_budgetcode         = local.budget_code
  # tag_owner              = local.owner
  # tag_projectname        = local.project
  # tag_systemtier         = "0"
  # tag_drtier             = "0"
  # tag_dataclassification = "N/A"
  # tag_notes              = "N/A"
  # tag_eol                = "N/A"
  # tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}

module "datanow_log_group" {
  source                 = "app.terraform.io/AMA/cloudwatch-group/aws"
  version                = "1.0.0"

  log_group_name         = "/ecs/datanow/${local.environment}"
  environment            = local.environment
  project                = lower(local.project)

  tag_name               = "${local.project}-${local.environment}-datanow-log-group"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}


#####################################################################
# Datalake - Data Linage Graph Database (Neptune)                   #
#####################################################################

module "neptune_lineage" {
  source                 = "app.terraform.io/AMA/neptune-cluster/aws"
  version                = "1.0.0"

  count = var.create_neptune ? 1 : 0

  app_name               = lower(local.project)
  instance_id            = lower(local.project)
  neptune_subnet_list    = data.terraform_remote_state.infrastructure.outputs.subnet_ids
  security_group_ids     = [module.neptune_sg.security_group_id]
  environment            = local.environment

  tag_name               = "${local.project}-${local.environment}-neptune-cluster"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}

module "neptune_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "${local.project}-${local.environment}-neptune-sg"
  description = "Security group for the Neptune ${local.project} VPC interfaces"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "8182"
      to_port     = "8182"
      protocol    = "tcp"
      description = "Neptune (Gremlin)"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
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

  tags = merge(local.tags, { Name = "${upper(local.project)}-${upper(local.environment)}-NEPTUNE-SG" })
  # tag_name               = "${local.project}-${local.environment}-neptune-cluster"
  # tag_environment        = local.environment
  # tag_contact            = local.contact
  # tag_budgetcode         = local.budget_code
  # tag_owner              = local.owner
  # tag_projectname        = local.project
  # tag_systemtier         = "0"
  # tag_drtier             = "0"
  # tag_dataclassification = "N/A"
  # tag_notes              = "N/A"
  # tag_eol                = "N/A"
  # tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}


#####################################################################
# Datalake - Dynamo DB                                              #
#####################################################################

module "dynamodb_scheduler_locks" {
  source                             = "app.terraform.io/AMA/dynamodb-table/aws"
  version                            = "1.0.0"
  name                               = "${local.project}-scheduler-locks-${local.environment}"
  billing_mode                       = "PAY_PER_REQUEST"
  hash_key                           = "LockID"
  stream_enabled                     = "false"
  ttl_enabled                        = "true"
  ttl_attribute_name                 = "ttl"
  server_side_encryption_enabled     = "true"
  server_side_encryption_kms_key_arn = aws_kms_key.key.arn
  attributes = [
    {
      name = "LockID"
      type = "S"
    }
  ]
  tag_name               = "${local.project}-${local.environment}-dynamodb"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags                   = {}
}

module "dynamodb_dag_configuration" {
  source                             = "app.terraform.io/AMA/dynamodb-table/aws"
  version                            = "1.0.0"
  name                               = "${local.project}-configuration-${local.environment}"
  billing_mode                       = "PAY_PER_REQUEST"
  hash_key                           = "DAG"
  range_key                          = "Task"
  stream_enabled                     = "false"
  ttl_enabled                        = "true"
  ttl_attribute_name                 = "ttl"
  server_side_encryption_enabled     = "true"
  server_side_encryption_kms_key_arn = aws_kms_key.key.arn
  attributes = [
    {
      name = "DAG"
      type = "S"
    },
    {
      name = "Task"
      type = "S"
    }
  ]
  tag_name               = "${local.project}-${local.environment}-dynamodb"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags                   = {}
}


module "dynamodb_dag_state" {
  source                             = "app.terraform.io/AMA/dynamodb-table/aws"
  version                            = "1.0.0"
  name                               = "${local.project}-dag-state-${local.environment}"
  billing_mode                       = "PAY_PER_REQUEST"
  hash_key                           = "name"
  range_key                          = "execution_time"
  stream_enabled                     = "false"
  ttl_enabled                        = "true"
  ttl_attribute_name                 = "ttl"
  server_side_encryption_enabled     = "true"
  server_side_encryption_kms_key_arn = aws_kms_key.key.arn
  attributes = [
    {
      name = "name"
      type = "S"
    },
    {
      name = "execution_time"
      type = "S"
    }
  ]

  tag_name               = "${local.project}-${local.environment}-dynamodb"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
  tags                   = {}
}


#####################################################################
# Web App Load Balancer
#####################################################################

module "webapp_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "${local.project}-${local.environment}-webapp-sg"
  description = "Security group for DataLabs web app load balancer"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

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

  tags = merge(local.tags, { Name = "${upper(local.project)}-${upper(local.environment)}-WEBAPP-ALB-SG" })
  # tag_name               = "${upper(local.project)}-${upper(local.environment)}-WEBAPP-ALB-SG"
  # tag_environment        = local.environment
  # tag_contact            = local.contact
  # tag_budgetcode         = local.budget_code
  # tag_owner              = local.owner
  # tag_projectname        = local.project
  # tag_systemtier         = "0"
  # tag_drtier             = "0"
  # tag_dataclassification = "N/A"
  # tag_notes              = "N/A"
  # tag_eol                = "N/A"
  # tag_maintwindow        = "N/A"
  # tags = {
  #   Group      = local.group
  #   Department = local.department
  # }
}

module "webapp_alb" {
  source                           = "app.terraform.io/AMA/alb/aws"
  version                          = "1.0.2"
  environment                      = local.environment
  name                             = "webapp"
  project                          = lower(local.project)
  description                      = "DataLabs Web APP Load Balancer"
  vpc_id                           = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
  security_groups                  = [module.webapp_sg.security_group_id]
  internal                         = true
  load_balancer_type               = "application"
  subnet_ids                       = data.terraform_remote_state.infrastructure.outputs.subnet_ids
  enable_deletion_protection       = "false"
  target_type                      = "ip"
  target_group_port                = 80
  target_group_protocol            = "HTTP"
  listener_port                    = 443
  listener_protocol                = "HTTPS"
  ssl_policy                       = "ELBSecurityPolicy-2020-10"
  certificate_arn                  = var.public_certificate_arn
  action                           = "forward"
  health_check_protocol            = "HTTP"
  health_check_port                = 80
  health_check_interval            = 300
  health_check_path                = "/"
  health_check_timeout             = "3"
  health_check_healthy_threshold   = "5"
  health_check_unhealthy_threshold = "10"
  health_check_matcher             = "200"

  tag_name                         = "${local.project}-${local.environment}-webapp-alb"
  tag_environment                  = local.environment
  tag_contact                      = local.contact
  tag_budgetcode                   = local.budget_code
  tag_owner                        = local.owner
  tag_projectname                  = local.project
  tag_systemtier                   = "0"
  tag_drtier                       = "0"
  tag_dataclassification           = "N/A"
  tag_notes                        = "N/A"
  tag_eol                          = "N/A"
  tag_maintwindow                  = "N/A"
  tags = {
    Group      = local.group
    Department = local.department
  }
}


#####################################################################
# DataLake - CloudWatch Events
#####################################################################

resource "aws_cloudwatch_event_rule" "invoke_scheduler" {
  name                = "${local.project}-${local.environment}-invoke-scheduler"
  description         = "Trigger running of the scheduler periodically"
  schedule_expression = "cron(*/15 * * * ? *)"

  tags = merge(local.tags, { Name = "${local.project}-${local.environment}-scheduler-event" })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule = aws_cloudwatch_event_rule.invoke_scheduler.name
  arn  = module.sns_scheduler.topic_arn
}
