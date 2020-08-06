resource "aws_lambda_function" "etl_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name   = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = 30
    memory_size     = 1024
    kms_key_arn     = data.aws_kms_key.cpt.arn

    environment {
        variables = merge(local.variables, var.variables)
    }

    depends_on = [var.parent_function]

    tags = merge(local.tags, {Name = "${var.project} API ETL Lambda Function"})
}


data "aws_kms_key" "cpt" {
  key_id = "alias/DataLabs/${var.project}"
}


data "aws_ssm_parameter" "database_username" {
    name = "/DataLabs/${var.project}/RDS/username"
}


data "aws_ssm_parameter" "database_password" {
    name = "/DataLabs/${var.project}/RDS/password"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}


data "aws_caller_identity" "account" {}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


locals {
    na                  = "N/A"
    owner               = "DataLabs"
    tags = {
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = "Application"
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = "PBW"
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        Project             = var.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
    variables = {
        TASK_WRAPPER_CLASS      = "datalabs.etl.awslambda.ETLTaskWrapper"
        TASK_CLASS              = "datalabs.etl.task.ETLTask"
    }
}
