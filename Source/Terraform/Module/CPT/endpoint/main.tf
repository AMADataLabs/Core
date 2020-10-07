
resource "aws_lambda_function" "endpoint_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name   = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = var.timeout
    memory_size     = var.memory_size
    kms_key_arn     = data.aws_kms_key.cpt.arn

    environment {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.access.api.awslambda.APIEndpointTaskWrapper"
            TASK_CLASS              = var.task_class
            DATABASE_NAME           = var.database_name
            DATABASE_BACKEND        = var.database_backend
            DATABASE_HOST           = var.database_host
            DATABASE_USERNAME       = data.aws_ssm_parameter.database_username.arn
            DATABASE_PASSWORD       = data.aws_ssm_parameter.database_password.arn
            BUCKET_NAME             = data.aws_ssm_parameter.processed_bucket.arn
            BUCKET_BASE_PATH        = data.aws_ssm_parameter.s3_base_path.arn
            BUCKET_URL_DURATION     = "600"
        }
    }

    tags = merge(local.tags, {Name = "${var.project} API Endpoint Lambda Function"})
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
