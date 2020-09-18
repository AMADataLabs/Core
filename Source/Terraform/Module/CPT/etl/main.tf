resource "aws_lambda_function" "etl_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name   = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = var.timeout
    memory_size     = 1024
    kms_key_arn     = data.aws_kms_key.cpt.arn

    environment {
        variables = merge(local.variables, var.variables)
    }

    depends_on = [var.parent_function]

    tags = merge(local.tags, {Name = "${var.project} API ETL Lambda Function"})
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
