resource "aws_lambda_function" "ingestion_etl_router" {
    s3_bucket           = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key              = "CPT/CPT.zip"
    function_name       = local.function_names.ingestion_etl_router
    role                = aws_iam_role.lambda_role.arn
    handler             = "main.lambda_handler"
    runtime             = "python3.7"
    timeout             = 10
    memory_size         = 1024

    environment {
        variables = {
            TASK_WRAPPER_CLASS  = "datalabs.etl.cpt.router.RouterTaskWrapper"
            TASK_CLASS          = "datalabs.etl.cpt.router.RouterTask"
            ROUTER__BASE_PATH   = data.aws_ssm_parameter.s3_base_path.arn
            ROUTER__REGION      = local.region
            ROUTER__ACCOUNT     = data.aws_caller_identity.account.account_id
            ROUTER__FUNCTIONS   = "${local.function_names.convert},${local.function_names.bundlepdf}"
        }
    }

    tags = merge(local.tags, {Name = "${var.project} API Ingestion ETL Router"})
}


resource "aws_lambda_permission" "ingestion_etl_router" {
    statement_id    = "AllowSNSInvoke"
    action          = "lambda:InvokeFunction"
    function_name   = local.function_names.ingestion_etl_router
    principal       = "sns.amazonaws.com"
    source_arn      = data.aws_sns_topic.ingestion.arn
}


resource "aws_sns_topic_subscription" "ingestion_etl_router" {
  topic_arn = data.aws_sns_topic.ingestion.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.ingestion_etl_router.arn
}


resource "aws_lambda_function" "processed_etl_router" {
    s3_bucket           = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key              = "CPT/CPT.zip"
    function_name       = local.function_names.processed_etl_router
    role                = aws_iam_role.lambda_role.arn
    handler             = "main.lambda_handler"
    runtime             = "python3.7"
    timeout             = 5
    memory_size         = 1024

    environment {
        variables = {
            TASK_WRAPPER_CLASS  = "datalabs.etl.cpt.router.RouterTaskWrapper"
            TASK_CLASS          = "datalabs.etl.cpt.router.RouterTask"
            ROUTER__BASE_PATH   = data.aws_ssm_parameter.s3_base_path.arn
            ROUTER__REGION      = local.region
            ROUTER__ACCOUNT     = data.aws_caller_identity.account.account_id
            ROUTER__FUNCTIONS   = "${local.function_names.loaddb}"
        }
    }

    tags = merge(local.tags, {Name = "${var.project} API Processed ETL Router"})
}


resource "aws_lambda_permission" "processed_etl_router" {
    statement_id    = "AllowLambdaInvoke"
    action          = "lambda:InvokeFunction"
    function_name   = local.function_names.processed_etl_router
    principal       = "sns.amazonaws.com"
    source_arn      = data.aws_sns_topic.processed.arn
}


resource "aws_sns_topic_subscription" "processed_etl_router" {
  topic_arn = data.aws_sns_topic.processed.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.processed_etl_router.arn
}
