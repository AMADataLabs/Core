#####################################################################
# Datalake - Passwords
#####################################################################

resource "random_password" "etcd_scheduler_password" {
  length           = 16
  special          = true
  override_special = "_%" #Supply your own list of special characters to use (if application can only handle certain special characters)
  # Reference with random_password.etcd_scheduler_password.result
}


#####################################################################
# Datalake - CloudWatch Events
#####################################################################

resource "aws_cloudwatch_event_rule" "scheduler_trigger" {
  name                = "${var.project}-${local.environment}-invoke-scheduler"
  description         = "Trigger running of the scheduler periodically"
  schedule_expression = "cron(*/15 * * * ? *)"

  tags = merge(local.tags, { Name = "Data Lake Scheduler Periodic Trigger" })
}

resource "aws_cloudwatch_event_target" "sns" {
  rule = aws_cloudwatch_event_rule.scheduler_trigger.name
  arn  = module.sns_scheduler_topic.topic_arn
}


#####################################################################
# Datalake - DynamoDB Instances and Tables
#####################################################################

resource "aws_dynamodb_table" "scheduler_locks" {
  name         = "${var.project}-scheduler-locks-${local.environment}"
  billing_mode = "PAY_PER_REQUEST"
  # read_capacity   = 10
  # write_capacity  = 2
  hash_key = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(local.tags, { Name = "Data Labs DAG Scheduler Lock Table" })
}


resource "aws_dynamodb_table" "configuration" {
  name         = "${var.project}-configuration-${local.environment}"
  billing_mode = "PAY_PER_REQUEST"
  # read_capacity   = 10
  # write_capacity  = 2
  hash_key  = "DAG"
  range_key = "Task"

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

  tags = merge(local.tags, { Name = "Data Labs Task Configuration Table" })
}


resource "aws_dynamodb_table" "dag_state" {
  name         = "${var.project}-dag-state-${local.environment}"
  billing_mode = "PAY_PER_REQUEST"
  # read_capacity  = 10
  # write_capacity = 2
  hash_key  = "name"
  range_key = "execution_time"

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

  tags = merge(local.tags, { Name = "Data Labs DAG State Table" })
}
