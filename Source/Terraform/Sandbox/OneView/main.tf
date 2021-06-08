provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


# Generate a new random password with the "random" provider
resource "random_password" "database_password" {
  length = 16
  special = true
  override_special = "_%" #Supply your own list of special characters to use (if application can only handle certain special characters)
  # Reference with random_password.database_password.result
}


# module "oneview" {
#     source = "../../Module/OneView"
#
#     rds_instance_class      = "db.m5.large"
#     rds_storage_type        = "gp2"
#     project                 = local.project
#     endpoint_memory_size    = 3072
# }

#
# module "rds_instance" {
#   source  = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-rds.git?ref=2.0.1"
#   db_instance_class                 = var.db_instance_class
#   enable_iops                       = false
#   auto_minor_version_upgrade        = false
#   apply_immediately                 = true
#   db_instance_port                  = 5432
#   vpc_security_group_list           = [module.rds_sg.security_group_id]
#   db_subnet_list                    = data.terraform_remote_state.dev-infra.outputs.subnet_ids
#   create_initial_db                 = false
#   use_snapshot                      = false
#   db_instance_allocated_storage     = var.db_instance_allocated_storage
#   db_engine                         = "postgres"
#   use_engine_version                = true
#   db_engine_version                 = var.db_engine_version
#   use_custom_param_group            = false
#   max_allocated_storage             = var.max_allocated_storage
#   enable_multi_az                   = false
#   enable_insights                   = true
#   database_username                 = var.database_username
#   database_password                 = random_password.database_password.result
#   app_name                          = lower(var.project)
#   app_environment                   = var.environment
#   tag_name                          = "CPT API Database"
#   tag_environment                   = var.environment
#   tag_contact                       = var.contact
#   tag_budgetcode                    = var.budget_code
#   tag_owner                         = var.owner
#   tag_projectname                   = var.project
#   tag_systemtier                    = "0"
#   tag_drtier                        = "0"
#   tag_dataclassification            = "N/A"
#   tag_notes                         = "N/A"
#   tag_eol                           = "N/A"
#   tag_maintwindow                   = "N/A"
# }


resource "aws_db_instance" "oneview_database" {
    identifier                    = "${var.project}-${var.environment}"
    instance_class                = var.rds_instance_class
    storage_type                  = var.rds_storage_type
    port                          = 5432
    allocated_storage             = 20
    engine                        = "postgres"
    engine_version                = var.db_engine_version
    max_allocated_storage         = 1000
    publicly_accessible           = true
    copy_tags_to_snapshot         = true
    performance_insights_enabled  = true
    skip_final_snapshot           = true
    username                      = var.database_username
    password                      = random_password.database_password.result

    tags = merge(local.tags, {Name = "${var.project} Database"})
}


module "etl_lambda" {
    source              = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name       = local.function_names.etl
    lambda_name         = local.function_names.etl
    s3_lambda_bucket    = var.lambda_code_bucket
    s3_lambda_key       = "OneView.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = var.etl_memory_size
    timeout             = var.etl_timeout

    lambda_policy_vars  = {
        account_id                  = var.account
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = true
    api_arn                     = "arn:aws-partition:service:${local.region}:${var.account}:resource-id"

    environment_variables = {
        variables = {
          TASK_WRAPPER_CLASS      = "datalabs.awslambda.TaskWrapper"
          ETCD_HOST               = var.etcd_host
          ETCD_USERNAME           = "scheduler"
          ETCD_PASSWORD           = random_password.etcd_scheduler_password.result
          ETCD_PREFIX             = "TASK_PROCESSOR_"
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
