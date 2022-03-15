#Get the running execution context
data "aws_caller_identity" "account" {}

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

  tag_name               = local.topic_names.scheduler
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


resource "aws_sns_topic_subscription" "scheduler" {
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
    s3_bucket_name = "not_applicable"
  }

  name               = local.topic_names.dag_processor
  topic_display_name = local.topic_names.dag_processor
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = local.topic_names.dag_processor
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


resource "aws_sns_topic_subscription" "dag_processor" {
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
    s3_bucket_name = "not_applicable"
  }

  name               = local.topic_names.task_processor
  topic_display_name = local.topic_names.task_processor
  app_name           = lower(local.project)
  app_environment    = local.environment

  tag_name               = local.topic_names.task_processor
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


resource "aws_sns_topic_subscription" "task_processor" {
  topic_arn = module.sns_task.topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_task_processor.function_arn
}


#####################################################################
# Datalake - ECS Cluster, Service, and Task Definitions             #
#####################################################################


module "datalake_ecs_cluster" {
  source          = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-fargate.git?ref=2.0.0"
  app_name        = lower(local.project)
  app_environment = local.environment

  tag_name               = "${upper(local.project)}-${local.environment}-ECS-CLUSTER"
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


resource "aws_ecs_service" "datanow" {
  name                              = "DataNow"
  task_definition                   = module.datanow_task_definition.aws_ecs_task_definition_td_arn
  launch_type                       = "FARGATE"
  cluster                           = module.datalake_ecs_cluster.ecs_cluster_id
  desired_count                     = 1
  platform_version                  = "1.4.0"
  health_check_grace_period_seconds = 0
  propagate_tags                    = "TASK_DEFINITION"

  deployment_controller {
    type = "ECS"
  }

  timeouts {}

  network_configuration {
    assign_public_ip = true

    security_groups = [
      module.datanow_alb_sg.security_group_id
    ]

    subnets = data.terraform_remote_state.infrastructure.outputs.subnet_ids
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.datanow.arn
    container_name   = "datanow"
    container_port   = "9047"
  }


  tags = merge(local.tags, { Name = "Data Labs Data Lake DataNow Service" })

  depends_on = [
    module.datanow_task_definition,
    aws_lb_target_group.datanow
  ]
}


module "datanow_task_definition" {
  source             = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-ecs-fargate-task-definition.git?ref=2.0.0"
  task_name          = "datanow"
  environment_name   = local.environment
  execution_role_arn = aws_iam_role.datanow_execution.arn
  task_role_arn      = aws_iam_role.datanow_task.arn
  container_cpu      = 1024
  container_memory   = 8192

  container_definition_vars = {
    account_id = local.account,
    region     = local.region
    image      = local.datanow_image
    tag        = var.datanow_version
  }

  volume = [
    {
      name = "DataNow"

      efs_volume_configuration = [
        {
          "file_system_id" : module.datanow_efs.filesystem_id
          "root_directory" : "/"
          "transit_encryption" : "ENABLED"

          "authorization_config" : {
            "access_point_id" : module.datanow_efs.access_point_id
            "iam" : "ENABLED"
          }
        }
      ]
    }
  ]

  tag_name               = "${local.project} DataNow Task"
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


resource "aws_alb" "datanow" {
  name               = "DataNow"
  internal           = false # Internet-facing. Requires an Internet Gateway
  load_balancer_type = "application"

  subnets = data.terraform_remote_state.infrastructure.outputs.public_subnet_ids

  security_groups = [
    module.datanow_alb_sg.security_group_id,
  ]

  tags = merge(local.tags, { Name = "Data Lake DataNow Load Balancer" })
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
  name        = "${local.project}DataNow"
  port        = 9047
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  health_check {
    enabled             = true
    path                = "/apiv2/server_status"
    healthy_threshold   = 5
    unhealthy_threshold = 2
  }

  tags = merge(local.tags, { Name = "DataLake-sbx-datanow-tg" })
}


module "datanow_alb_sg" {
  source = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-security-group.git?ref=1.0.0"

  name        = "${lower(local.project)}-${local.environment}-datanow"
  description = "Security group for Datanow"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

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

  tags = merge(local.tags, { Name = "Data Lake DataNow Security Group" })
}


resource "aws_cloudwatch_log_group" "datanow" {
  name = "/ecs/datanow"

  tags = merge(local.tags, { Name = "Data Lake DataNow Log Group" })
}


resource "aws_iam_role" "datanow_task" {
  name = "${local.project}DataNowAssumeRole"

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


resource "aws_iam_role" "datanow_execution" {
  name = "${local.project}DataNowExecutionRole"

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

  tags = merge(local.tags, { Name = "DataLake-sbx-datanow-ecs-task-execution-role" })
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

  tags = merge(local.tags, { Name = "DataLake-sbx-datanow-ecs-task-execution-policy" })
}
# "Condition": {
#     "StringEquals": {
#         "aws:sourceVpce": "${aws_vpc_endpoint.ecr.id}"
#     }
# }

resource "aws_iam_role_policy_attachment" "datanow_execution" {
  role       = aws_iam_role.datanow_execution.name
  policy_arn = aws_iam_policy.ecs_task_execution.arn
}


#####################################################################
# Datalake - EFS Volume                                             #
#####################################################################

module "datanow_efs" {
  source            = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-efs.git?ref=2.0.0"
  performance_mode  = "generalPurpose"
  transition_to_ia  = "AFTER_14_DAYS"
  posix_user_gid    = 999
  posix_user_uid    = 999
  path_permissions  = 755
  access_point_path = "/dremio"
  app_name          = lower(local.project)
  app_environment   = local.environment
  subnet_ids        = data.terraform_remote_state.infrastructure.outputs.public_subnet_ids
  security_groups   = [module.datanow_alb_sg.security_group_id]

  tag_name               = "${local.project}-${local.environment}-datanow-efs"
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
# Datalake - Neptune Cluster                                        #
#####################################################################


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
}



#Don't forget to update tags
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
  tags                   = {}
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
  source      = "app.terraform.io/AMA/security-group/aws"
  version     = "1.0.0"
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

  tags = merge(local.tags, { Name = "DataLabs web app load balancer security group" })
}

module "webapp_alb" {
  source      = "app.terraform.io/AMA/alb/aws"
  version     = "1.0.2"
  environment = local.environment
  name        = "webapp"
  project     = lower(local.project)
  description = "DataLabs Web APP Load Balancer"
  # vpc_id                            = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
  vpc_id = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
  # security_groups                   = [module.oneview_sg.security_group_id]
  security_groups    = [module.webapp_sg.security_group_id]
  internal           = true
  load_balancer_type = "application"
  # subnet_ids                        = local.subnets
  subnet_ids                 = data.terraform_remote_state.infrastructure.outputs.public_subnet_ids
  enable_deletion_protection = "false"
  target_type                = "ip"
  target_group_port          = 80
  target_group_protocol      = "HTTP"
  listener_port              = 443
  listener_protocol          = "HTTPS"
  ssl_policy                 = "ELBSecurityPolicy-2020-10"
  # certificate_arn                   = var.private_certificate_arn
  certificate_arn                  = data.aws_acm_certificate.amaaws.arn
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
  tags                             = {}
}


#####################################################################
# Datalake - CloudWatch Events
#####################################################################

resource "aws_cloudwatch_event_rule" "scheduler_trigger" {
  name                = "${local.project}-${local.environment}-invoke-scheduler"
  description         = "Trigger running of the scheduler periodically"
  schedule_expression = "cron(*/15 * * * ? *)"

  tags = merge(local.tags, { Name = "Data Lake Scheduler Periodic Trigger" })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule = aws_cloudwatch_event_rule.scheduler_trigger.name
  arn  = module.sns_scheduler.topic_arn
}
