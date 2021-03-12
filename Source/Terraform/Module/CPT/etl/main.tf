module "etl_lambda" {
    # source                    = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git"
    source                      = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name               = var.function_name
    s3_lambda_bucket            = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_lambda_key               = "CPT/CPT.zip"
    handler                     = "awslambda.handler"
    runtime                     = local.runtime
    create_alias                = false
    memory_size                 = var.memory_size
    timeout                     = var.timeout

    lambda_name                 = var.function_name
    lambda_policy_vars          = {
        account_id                  = var.account_id
        region                      = var.region
        project                     = var.project
    }

    create_lambda_permission    = false
    api_arn                     = ""

    environment_variables       = {
        variables                   = merge(local.variables, var.variables)
    }

    tag_name                    = "${var.project} API ETL Lambda Function"
    tag_environment             = local.tags["Env"]
    tag_contact                 = local.tags["Contact"]
    tag_systemtier              = local.tags["SystemTier"]
    tag_drtier                  = local.tags["DRTier"]
    tag_dataclassification      = local.tags["DataClassification"]
    tag_budgetcode              = local.tags["BudgetCode"]
    tag_owner                   = local.tags["Owner"]
    tag_projectname             = var.project
    tag_notes                   = local.tags["Notes"]
    tag_eol                     = local.tags["EOL"]
    tag_maintwindow             = local.tags["MaintenanceWindow"]
}




# resource "aws_lambda_function" "etl_lambda" {
#     s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
#     s3_key          = "CPT/CPT.zip"
#     function_name   = var.function_name
#     role            = var.role
#     handler         = "awslambda.handler"
#     runtime         = "python3.7"
#     timeout         = var.timeout
#     memory_size     = 1024
#     kms_key_arn     = data.aws_kms_key.cpt.arn
#
#     environment {
#         variables = merge(local.variables, var.variables)
#     }
#
#     depends_on = [var.parent_function]
#
#     tags = merge(local.tags, {Name = "${var.project} API ETL Lambda Function"})
# }


locals {
    na                  = "N/A"
    owner               = "DataLabs"
    runtime             = "python3.7"
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
        Notes               = ""
    }
    variables = {
        TASK_WRAPPER_CLASS      = "datalabs.etl.awslambda.ETLTaskWrapper"
        TASK_CLASS              = "datalabs.etl.task.ETLTask"
    }
}
