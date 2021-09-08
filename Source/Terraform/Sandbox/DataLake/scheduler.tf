#####################################################################
# Datalake - Passwords
#####################################################################

resource "random_password" "etcd_scheduler_password" {
  length = 16
  special = true
  override_special = "_%" #Supply your own list of special characters to use (if application can only handle certain special characters)
  # Reference with random_password.etcd_scheduler_password.result
}


#####################################################################
# Datalake - S3 Buckets
#####################################################################

module "s3_scheduler_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-datalake-scheduler-data-${var.region}"

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

  tag_name                          = "${var.project}-${var.environment}-s3-scheduler-data"
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


resource "aws_s3_bucket_notification" "sns_scheduler" {
    bucket = module.s3_scheduler_data.bucket_id
    topic {
        topic_arn           = module.sns_scheduler_topic.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


#####################################################################
# Datalake - SNS Topics and Subscriptions
#####################################################################

module "sns_scheduler_topic" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = local.topic_names.scheduler
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_scheduler_data.bucket_id
  }

  name = local.topic_names.scheduler
  topic_display_name    = local.topic_names.scheduler
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                         = local.topic_names.scheduler
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


resource "aws_sns_topic_subscription" "scheduler" {
  topic_arn = module.sns_scheduler_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.dag_processor_lambda.function_arn
}


module "sns_dag_topic" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = local.topic_names.dag_processor
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = "not_applicable"
  }

  name = local.topic_names.dag_processor
  topic_display_name    = local.topic_names.dag_processor
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                         = local.topic_names.dag_processor
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


resource "aws_sns_topic_subscription" "dag_processor" {
  topic_arn = module.sns_dag_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.dag_processor_lambda.function_arn
}


module "sns_task_topic" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = local.topic_names.task_processor
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = "not_applicable"
  }

  name = local.topic_names.task_processor
  topic_display_name    = local.topic_names.task_processor
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                         = local.topic_names.task_processor
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


resource "aws_sns_topic_subscription" "task_processor" {
  topic_arn = module.sns_task_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.task_processor_lambda.function_arn
}


#####################################################################
# Datalake - CloudWatch Events
#####################################################################

resource "aws_cloudwatch_event_rule" "console" {
  name        = "${var.project}-${var.environment}-invoke-scheduler"
  description = "Trigger running of the scheduler periodically"
  schedule_expression = "cron(*/15 * * * ? *)"

  event_pattern = <<EOF
{
  "detail-type": [
    "Run Scheduler Event"
  ]
}
EOF
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.console.name
  arn       = module.sns_scheduler_topic.topic_arn
}


#####################################################################
# Datalake - DynamoDB Instances and Tables
#####################################################################

resource "aws_dynamodb_table" "scheduler_locks" {
    name            = "${var.project}-scheduler-locks-${var.environment}"
    billing_mode    = "PAY_PER_REQUEST"
    # read_capacity   = 10
    # write_capacity  = 2
    hash_key        = "LockID"

    attribute {
        name = "LockID"
        type = "S"
    }

    ttl {
      attribute_name = "ttl"
      enabled        = true
    }

    tags = merge(local.tags, {Name = "Data Labs DAG Scheduler Lock Table"})
}


resource "aws_dynamodb_table" "configuration" {
    name            = "${var.project}-configuration-${var.environment}"
    billing_mode    = "PAY_PER_REQUEST"
    # read_capacity   = 10
    # write_capacity  = 2
    hash_key        = "DAG"
    range_key      = "Task"

    attribute {
        name = "DAG"
        type = "S"
    }

    attribute {
        name = "Task"
        type = "S"
    }

    ttl {
      attribute_name = "ttl"
      enabled        = true
    }

    tags = merge(local.tags, {Name = "Data Labs Task Configuration Table"})
}


resource "aws_dynamodb_table" "dag_state" {
    name            = "${var.project}-dag-state-${var.environment}"
    billing_mode    = "PAY_PER_REQUEST"
    # read_capacity  = 10
    # write_capacity = 2
    hash_key       = "name"
    range_key      = "execution_time"

    attribute {
        name = "name"
        type = "S"
    }

    attribute {
        name = "execution_time"
        type = "S"
    }

    ttl {
      attribute_name = "ttl"
      enabled        = true
    }

    tags = merge(local.tags, {Name = "Data Labs DAG State Table"})
}


#####################################################################
# Datalake - Lambda functions
#####################################################################

module "dag_processor_lambda" {
    source              = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name       = local.function_names.dag_processor
    lambda_name         = local.function_names.dag_processor
    s3_lambda_bucket    = var.lambda_code_bucket
    s3_lambda_key       = "Scheduler.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.scheduler_memory_size
    timeout             = var.scheduler_timeout

    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = false
    api_arn                     = ""

    environment_variables = {
        variables = {
          TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.ProcessorTaskWrapper"
          TASK_CLASS              = "datalabs.etl.dag.process.DAGProcessorTask"
          DYNAMODB_CONFIG_TABLE   = aws_dynamodb_table.configuration.id
        }
    }

    tag_name                = local.function_names.dag_processor
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


module "task_processor_lambda" {
    source              = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name       = local.function_names.task_processor
    lambda_name         = local.function_names.task_processor
    s3_lambda_bucket    = var.lambda_code_bucket
    s3_lambda_key       = "Scheduler.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.scheduler_memory_size
    timeout             = var.scheduler_timeout

    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = false
    api_arn                     = ""

    environment_variables = {
        variables = {
          TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.ProcessorTaskWrapper"
          TASK_CLASS              = "datalabs.etl.dag.process.TaskProcessorTask"
          DYNAMODB_CONFIG_TABLE   = aws_dynamodb_table.configuration.id
        }
    }

    tag_name                = local.function_names.task_processor
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

module "scheduler_lambda" {
    source              = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name       = local.function_names.scheduler
    lambda_name         = local.function_names.scheduler
    s3_lambda_bucket    = var.lambda_code_bucket
    s3_lambda_key       = "Scheduler.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.scheduler_memory_size
    timeout             = var.scheduler_timeout

    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = false
    api_arn                     = ""

    environment_variables = {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.DAGTaskWrapper"
            TASK_RESOLVER_CLASS     = "datalabs.etl.dag.resolve.TaskResolver"
            DYNAMODB_CONFIG_TABLE   = aws_dynamodb_table.configuration.id
            DAG_CLASS               = "datalabs.etl.dag.schedule.dag.DAGSchedulerDAG"
        }
    }

    tag_name                = local.function_names.scheduler
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


resource "aws_lambda_permission" "dag_processor_scheduler_sns" {
  statement_id  = "AllowSNSInvokefor-Scheduler"
  action        = "lambda:InvokeFunction"
  function_name = module.dag_processor_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn = module.sns_scheduler_topic.topic_arn
  depends_on = [ module.dag_processor_lambda ]
}


resource "aws_lambda_permission" "dag_processor_sns" {
  statement_id  = "AllowSNSInvokefor-${module.dag_processor_lambda.function_name}"
  action        = "lambda:InvokeFunction"
  function_name = module.dag_processor_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn = module.sns_dag_topic.topic_arn
  depends_on = [ module.dag_processor_lambda ]
}


resource "aws_lambda_permission" "task_processor_sns" {
  statement_id  = "AllowSNSInvokefor-${module.task_processor_lambda.function_name}"
  action        = "lambda:InvokeFunction"
  function_name = module.task_processor_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn = module.sns_task_topic.topic_arn
  depends_on = [ module.task_processor_lambda ]
}
