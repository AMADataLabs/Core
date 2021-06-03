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


resource "aws_s3_bucket_notification" "sns_scheduler_data" {
    bucket = module.s3_scheduler_data.bucket_id
    topic {
        topic_arn           = module.sns_scheduler_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


#####################################################################
# Datalake - SNS Topics and Subscriptions
#####################################################################


module "sns_scheduler_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = "scheduler_data-${var.environment}"
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_scheduler_data.bucket_id
  }

  name = "scheduler_data-${var.environment}"
  topic_display_name    = "scheduler_data-${var.environment}"
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                         = "${var.project}-${var.environment}-sns-scheduler-data"
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
# Datalake - DynamoDB Instances and Tables
#####################################################################

resource "aws_dynamodb_table" "scheduler_locks" {
    name            = "${var.project}-${var.environment}-scheduler-locks"
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

resource "aws_dynamodb_table" "dag_state" {
    name            = "${var.project}-${var.environment}-dag-state"
    billing_mode    = "PAY_PER_REQUEST"
    # read_capacity  = 10
    # write_capacity = 2
    hash_key       = "name"

    attribute {
        name = "name"
        type = "S"
    }

    ttl {
      attribute_name = "ttl"
      enabled        = true
    }

    tags = merge(local.tags, {Name = "Data Labs DAG State Table"})
}

resource "aws_dynamodb_table" "task_state" {
    name            = "${var.project}-${var.environment}-task-state"
    billing_mode    = "PAY_PER_REQUEST"
    # read_capacity  = 10
    # write_capacity = 2
    hash_key       = "name"
    range_key      = "DAG"

    attribute {
        name = "name"
        type = "S"
    }

    attribute {
        name = "DAG"
        type = "S"
    }

    ttl {
      attribute_name = "ttl"
      enabled        = true
    }

    tags = merge(local.tags, {Name = "Data Labs Task State Table"})
}


#####################################################################
# Datalake - Lambda functions
#####################################################################
