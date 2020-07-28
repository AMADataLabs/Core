data "archive_file" "etl_router" {
    type            = "zip"
    output_path     = "/tmp/etl_router.zip"
    source {
        content     = <<EOF
import json
import os

import boto3

client = boto3.client('lambda')

def lambda_handler(event,context):
    region = os.environ['REGION']
    account = os.environ['ACCOUNT']
    functions = os.environ['FUNCTIONS'].split(',')

    for function in functions:
        response = client.invoke(
            FunctionName = f'arn:aws:lambda:{region}:{account}:function:{function}',
            InvocationType = 'RequestResponse',
            Payload = json.dumps({})
        )
EOF
    filename = "main.py"
  }
}


resource "aws_lambda_function" "ingestion_etl_router" {
    filename            = data.archive_file.etl_router.output_path
    source_code_hash    = data.archive_file.etl_router.output_base64sha256
    function_name       = local.function_names.ingestion_etl_router
    role                = aws_iam_role.lambda_role.arn
    handler             = "main.lambda_handler"
    runtime             = "python3.7"
    timeout             = 5
    memory_size         = 1024

    environment {
        variables = {
            REGION      = local.region
            ACCOUNT     = data.aws_caller_identity.account.account_id
            FUNCTIONS   = "${local.function_names.convert},${local.function_names.bundlepdf}"
        }
    }

    tags = merge(local.tags, {Name = "CPT API Ingestion ETL Router"})
}


resource "aws_lambda_permission" "ingestion_etl_router" {
    statement_id    = "AllowS3Invoke"
    action          = "lambda:InvokeFunction"
    function_name   = local.function_names.ingestion_etl_router
    principal       = "s3.amazonaws.com"
    source_arn      = "arn:aws:sns:::${data.aws_sns_topic.ingestion.name}"
}


resource "aws_lambda_function" "processed_etl_router" {
    filename            = data.archive_file.etl_router.output_path
    source_code_hash    = data.archive_file.etl_router.output_base64sha256
    function_name       = local.function_names.processed_etl_router
    role                = aws_iam_role.lambda_role.arn
    handler             = "main.lambda_handler"
    runtime             = "python3.7"
    timeout             = 5
    memory_size         = 1024

    environment {
        variables = {
            REGION      = local.region
            ACCOUNT     = data.aws_caller_identity.account.account_id
            FUNCTIONS   = "${local.function_names.loaddb}"
        }
    }

    tags = merge(local.tags, {Name = "CPT API Processed ETL Router"})
}


resource "aws_lambda_permission" "processed_etl_router" {
    statement_id    = "AllowS3Invoke"
    action          = "lambda:InvokeFunction"
    function_name   = local.function_names.processed_etl_router
    principal       = "s3.amazonaws.com"
    source_arn      = "arn:aws:sns:::${data.aws_sns_topic.processed.name}"
}


data "aws_sns_topic" "ingestion" {
    name = "IngestionBucketNotification"
}


data "aws_sns_topic" "processed" {
    name = "ProcessedBucketNotification"
}
