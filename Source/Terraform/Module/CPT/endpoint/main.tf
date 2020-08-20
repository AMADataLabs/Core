
resource "aws_lambda_function" "endpoint_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name   = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = 15
    memory_size     = 1024
    kms_key_arn     = data.aws_kms_key.cpt.arn

    environment {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.access.api.awslambda.APIEndpointTaskWrapper"
            TASK_CLASS              = var.task_class
            DATABASE_NAME           = var.database_name
            DATABASE_BACKEND        = var.database_backend
            DATABASE_HOST           = var.database_host
            DATABASE_USERNAME       = data.aws_ssm_parameter.database_username.value
            DATABASE_PASSWORD       = data.aws_ssm_parameter.database_password.value
            BUCKET_NAME             = data.aws_ssm_parameter.processed_bucket.value
            BUCKET_BASE_PATH        = data.aws_ssm_parameter.s3_base_path.value
            BUCKET_URL_DURATION     = "600"
        }
    }

    tags = merge(local.tags, {Name = "${var.project} API Endpoint Lambda Function"})
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


data "aws_ssm_parameter" "processed_bucket" {
    name = "/DataLabs/DataLake/processed_bucket"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}


data "aws_ssm_parameter" "s3_base_path" {
    name  = "/DataLabs/${var.project}/s3/base_path"
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
}
