data "archive_file" "etl_router" {
    type            = "zip"
    output_path     = "/tmp/etl_router.zip"

    source {
        filename    = "main.py"
        content     = <<EOF
import json
import os

import boto3

client = boto3.client('lambda')

def lambda_handler(event, context):
    for sns_record in event['Records']:
        sns_envelope = sns_record['Sns']
        message = json.loads(sns_envelope['Message'])
        sqs_records = message['Records']

        for sqs_record in sqs_records:
            key = sqs_record['s3']['object']['key']
            print(f'Object updated: {key}')

            if key.startswith('AMA/CPT/') and key.endswith('ETL_TRIGGER'):
                _trigger_etls()

    return 200, None

def _trigger_etls():
    region = os.environ['REGION']
    account = os.environ['ACCOUNT']
    functions = os.environ['FUNCTIONS'].split(',')

    for function in functions:
        print(f'Invoking function: {function}')

        response = client.invoke(
            FunctionName = f'arn:aws:lambda:{region}:{account}:function:{function}',
            InvocationType = 'RequestResponse',
            Payload = json.dumps({})
        )
EOF
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


data "aws_sns_topic" "ingestion" {
    name = "IngestionBucketNotification"
}


data "aws_sns_topic" "processed" {
    name = "ProcessedBucketNotification"
}
