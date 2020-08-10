
resource "aws_lambda_function" "authorizer_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name   = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = 5
    memory_size     = 1024

    environment {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.access.awslambda.AuthorizerLambdaTaskWrapper"
            TASK_CLASS              = var.task_class
            PASSPORT_URL            = var.passport_url
        }
    }

    tags = merge(local.tags, {Name = "${var.project} API Authorizer Lambda Function"})
}


resource "aws_api_gateway_authorizer" "api_gateway_authorizer"{
    name             = "gateway_authorizer"
    rest_api_id      = var.api_gateway_id
    authorizer_uri   = aws_lambda_function.authorizer_lambda.invoke_arn

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
