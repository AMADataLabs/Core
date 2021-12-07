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
# Datalake - SNS Topics and Subscriptions
#####################################################################

module "sns_scheduler_topic" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = local.topic_names.scheduler
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_scheduler.bucket_id
  }

  name = local.topic_names.scheduler
  topic_display_name    = local.topic_names.scheduler
  app_name              = lower(var.project)
  app_environment       = local.environment

  tag_name                         = local.topic_names.scheduler
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


resource "aws_sns_topic_subscription" "scheduler" {
  topic_arn = module.sns_scheduler_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_dag_processor.function_arn
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
  app_environment       = local.environment

  tag_name                         = local.topic_names.dag_processor
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


resource "aws_sns_topic_subscription" "dag_processor" {
  topic_arn = module.sns_dag_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.lambda_dag_processor.function_arn
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
  app_environment       = local.environment

  tag_name                         = local.topic_names.task_processor
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


resource "aws_sns_topic_subscription" "task_processor" {
  topic_arn = module.sns_task_topic.topic_arn
  protocol  = "lambda"
  endpoint  = module.task_processor_lambda.function_arn
}


#####################################################################
# Datalake - CloudWatch Events
#####################################################################

resource "aws_cloudwatch_event_rule" "scheduler_trigger" {
  name        = "${var.project}-${local.environment}-invoke-scheduler"
  description = "Trigger running of the scheduler periodically"
  schedule_expression = "cron(*/15 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "sns" {
  rule      = aws_cloudwatch_event_rule.scheduler_trigger.name
  arn       = module.sns_scheduler_topic.topic_arn
}


#####################################################################
# Datalake - DynamoDB Instances and Tables
#####################################################################

resource "aws_dynamodb_table" "scheduler_locks" {
    name            = "${var.project}-scheduler-locks-${local.environment}"
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
    name            = "${var.project}-configuration-${local.environment}"
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
    name            = "${var.project}-dag-state-${local.environment}"
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

# resource "aws_lambda_permission" "lambda_dag_processor_cloudwatch" {
#      statement_id    = "AllowCloudWatchSInvoke"
#      action          = "lambda:InvokeFunction"
#      function_name   = module.lambda_dag_processor.function_name
#      principal       = "events.amazonaws.com"
#      source_arn      = module.sns_scheduler.topic_arn
# }


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
  function_name = module.lambda_dag_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn = module.sns_scheduler_topic.topic_arn
  depends_on = [ module.lambda_dag_processor ]
}


resource "aws_lambda_permission" "dag_processor_sns" {
  statement_id  = "AllowSNSInvokefor-${module.lambda_dag_processor.function_name}"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_dag_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn = module.sns_dag_topic.topic_arn
  depends_on = [ module.lambda_dag_processor ]
}


resource "aws_lambda_permission" "task_processor_sns" {
  statement_id  = "AllowSNSInvokefor-${module.task_processor_lambda.function_name}"
  action        = "lambda:InvokeFunction"
  function_name = module.task_processor_lambda.function_name
  principal     = "sns.amazonaws.com"
  source_arn = module.sns_task_topic.topic_arn
  depends_on = [ module.task_processor_lambda ]
}
