
resource "aws_lambda_function" "endpoint_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = 5
    memory_size     = 1024

    environment {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.access.awslambda.APIEndpointTaskWrapper"
            TASK_CLASS              = var.task_class
            DATABASE_NAME           = var.database_name
            DATABASE_BACKEND        = var.database_backend
            DATABASE_HOST           = var.database_host
            DATABASE_USERNAME       = data.aws_ssm_parameter.database_username.value
            DATABASE_PASSWORD       = data.aws_ssm_parameter.database_password.value
        }
    }

    tags = merge(local.tags, {Name = "CPT API Lambda Function"})
}


data "aws_ssm_parameter" "database_username" {
    name = "/DataLabs/CPT/RDS/username"
}


data "aws_ssm_parameter" "database_password" {
    name = "/DataLabs/CPT/RDS/password"
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
    region              = "us-east-1"
    spec_title          = "CPT API"
    spec_description    = "CPT API Phase I"
    na                  = "N/A"
    tags = {
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = "Application"
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = "PBW"
        Owner               = "Data Labs"
        Notes               = ""
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
