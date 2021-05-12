module "ingestion_etl_router_lambda" {
    source                      = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name               = local.function_names.ingestion_etl_router
    s3_lambda_bucket            = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_lambda_key               = "CPT/CPT.zip"
    handler                     = "awslambda.handler"
    runtime                     = local.runtime
    create_alias                = false
    memory_size                 = 1024
    timeout                     = 10

    lambda_name                 = local.function_names.ingestion_etl_router
    lambda_policy_vars          = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = local.project
    }

    create_lambda_permission    = false
    api_arn                     = ""

    environment_variables       = {
        variables = {
            TASK_WRAPPER_CLASS  = "datalabs.etl.cpt.router.RouterTaskWrapper"
            TASK_CLASS          = "datalabs.etl.cpt.router.RouterTask"
            ROUTER__BASE_PATH   = data.aws_ssm_parameter.s3_base_path.arn
            ROUTER__REGION      = local.region
            ROUTER__ACCOUNT     = data.aws_caller_identity.account.account_id
            ROUTER__FUNCTIONS   = "${local.function_names.convert},${local.function_names.bundlepdf}"
        }
    }

    tag_name                    = "${var.project} API Ingestion ETL Router"
    tag_environment             = local.tags["Env"]
    tag_contact                 = local.tags["Contact"]
    tag_systemtier              = local.tags["SystemTier"]
    tag_drtier                  = local.tags["DRTier"]
    tag_dataclassification      = local.tags["DataClassification"]
    tag_budgetcode              = local.tags["BudgetCode"]
    tag_owner                   = local.tags["Owner"]
    tag_projectname             = var.project
    tag_notes                   = ""
    tag_eol                     = local.tags["EOL"]
    tag_maintwindow             = local.tags["MaintenanceWindow"]
}


resource "aws_lambda_permission" "ingestion_etl_router" {
    statement_id    = "AllowSNSInvoke"
    action          = "lambda:InvokeFunction"
    function_name   = local.function_names.ingestion_etl_router
    principal       = "sns.amazonaws.com"
    source_arn      = data.aws_sns_topic.ingested_data.arn
}


resource "aws_sns_topic_subscription" "ingestion_etl_router" {
  topic_arn = data.aws_sns_topic.ingested_data.arn
  protocol  = "lambda"
  endpoint  = module.ingestion_etl_router_lambda.function_arn
}


module "processing_etl_router_lambda" {
    source                      = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=2.0.0"
    function_name               = local.function_names.processing_etl_router
    s3_lambda_bucket            = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_lambda_key               = "CPT/CPT.zip"
    handler                     = "awslambda.handler"
    runtime                     = local.runtime
    create_alias                = false
    memory_size                 = 1024
    timeout                     = 10

    lambda_name                 = local.function_names.processing_etl_router
    lambda_policy_vars          = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = local.project
    }

    create_lambda_permission    = false
    api_arn                     = ""

    environment_variables       = {
        variables = {
            TASK_WRAPPER_CLASS  = "datalabs.etl.cpt.router.RouterTaskWrapper"
            TASK_CLASS          = "datalabs.etl.cpt.router.RouterTask"
            ROUTER__BASE_PATH   = data.aws_ssm_parameter.s3_base_path.arn
            ROUTER__REGION      = local.region
            ROUTER__ACCOUNT     = data.aws_caller_identity.account.account_id
            ROUTER__FUNCTIONS   = "${local.function_names.loaddb}"
        }
    }

    tag_name                    = "${var.project} API Processing ETL Router"
    tag_environment             = local.tags["Env"]
    tag_contact                 = local.tags["Contact"]
    tag_systemtier              = local.tags["SystemTier"]
    tag_drtier                  = local.tags["DRTier"]
    tag_dataclassification      = local.tags["DataClassification"]
    tag_budgetcode              = local.tags["BudgetCode"]
    tag_owner                   = local.tags["Owner"]
    tag_projectname             = var.project
    tag_notes                   = ""
    tag_eol                     = local.tags["EOL"]
    tag_maintwindow             = local.tags["MaintenanceWindow"]
}


resource "aws_lambda_permission" "processing_etl_router" {
    statement_id    = "AllowLambdaInvoke"
    action          = "lambda:InvokeFunction"
    function_name   = local.function_names.processing_etl_router
    principal       = "sns.amazonaws.com"
    source_arn      = data.aws_sns_topic.processed_data.arn
}


resource "aws_sns_topic_subscription" "processing_etl_router" {
  topic_arn = data.aws_sns_topic.processed_data.arn
  protocol  = "lambda"
  endpoint  = module.processing_etl_router_lambda.function_arn
}
