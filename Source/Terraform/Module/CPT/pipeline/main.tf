# resource "aws_sfn_state_machine" "data_pipeline" {
#   name     = "my-state-machine"
#   role_arn = var.role

#   definition = <<EOF
# {
#   "Comment": "A Hello World example of the Amazon States Language using an AWS Lambda Function",
#   "StartAt": "HelloWorld",
#   "States": {
#     "HelloWorld": {
#       "Type": "Task",
#       "Resource": "${aws_lambda_function.lambda.arn}",
#       "End": true
#     }
#   }
# }
# EOF
# }


# resource "aws_lambda_permission" "lambda_permissions_step" {
#     count = var.data_pipeline_ingestion ? 1 : 0

#     statement_id  = "AllowExecutionFromStepFunctions"
#     action        = "lambda:InvokeFunction"
#     function_name = var.function_name
#     principal     = "s3.amazonaws.com"
#     # source_arn    = data.aws_s3_bucket.ingested_data_bucket.arn

#     depends_on = [aws_lambda_function.etl_lambda]
# }
