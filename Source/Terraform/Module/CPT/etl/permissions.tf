# resource "aws_lambda_permission" "lambda_permissions_ingestion" {
#     count = var.data_pipeline_ingestion ? 1 : 0

#     statement_id  = "AllowExecutionFromS3Bucket"
#     action        = "lambda:InvokeFunction"
#     function_name = var.function_name
#     principal     = "s3.amazonaws.com"
#     source_arn    = data.aws_s3_bucket.ingestion_bucket.arn

#     depends_on = [aws_lambda_function.etl_lambda]
# }


# resource "aws_s3_bucket_notification" "bucket_notification_ingestion" {
#     count   = var.data_pipeline_ingestion ? 1 : 0

#     bucket  = data.aws_s3_bucket.ingestion_bucket.id

#     lambda_function {
#         lambda_function_arn = aws_lambda_function.etl_lambda.arn
#         events              = ["s3:ObjectCreated:*"]
#         filter_prefix       = "AMA/CPT/"
#     }

#     depends_on = [aws_lambda_permission.lambda_permissions_ingestion]
# }

# resource "aws_lambda_permission" "lambda_permissions_api" {
#     count = var.data_pipeline_api ? 1 : 0

#     statement_id  = "AllowExecutionFromS3Bucket"
#     action        = "lambda:InvokeFunction"
#     function_name = var.function_name
#     principal     = "s3.amazonaws.com"
#     source_arn    = data.aws_s3_bucket.processed_bucket.arn

#     depends_on = [aws_lambda_function.etl_lambda]
# }


# resource "aws_s3_bucket_notification" "bucket_notification_api" {
#     count   = var.data_pipeline_api ? 1 : 0

#     bucket  = data.aws_s3_bucket.processed_bucket.id

#     lambda_function {
#         lambda_function_arn = aws_lambda_function.etl_lambda.arn
#         events              = ["s3:ObjectCreated:*"]
#         filter_prefix       = "AMA/CPT/"
#     }

#     depends_on = [aws_lambda_permission.lambda_permissions_api]
# }


# data "aws_ssm_parameter" "ingestion_bucket" {
#     name = "/DataLabs/DataLake/ingestion_bucket"
# }


# data "aws_s3_bucket" "ingestion_bucket" {
#     bucket = data.aws_ssm_parameter.ingestion_bucket.value
# }


# data "aws_ssm_parameter" "processed_bucket" {
#     name = "/DataLabs/DataLake/processed_bucket"
# }


# data "aws_s3_bucket" "processed_bucket" {
#     bucket = data.aws_ssm_parameter.processed_bucket.value
# }
