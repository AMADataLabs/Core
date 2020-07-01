resource "aws_lambda_permission" "lambda_permissions" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_id}/*/*/*"
}


variable "function_name" {
    description = "AWS region"
    type        = string
}



variable "region" {
    description = "AWS region"
    type        = string
}


variable "account_id" {
    description = "AWS Account ID"
    type        = string
}


variable "api_gateway_id" {
    description = "API Gateway ID"
    type        = string
}
