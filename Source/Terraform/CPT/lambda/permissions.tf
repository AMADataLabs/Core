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



resource "aws_lambda_permission" "lambda_permissions_TEST" {
  count = var.function_name_TEST == "" ? 0 : 1

  statement_id  = "AllowExecutionFromAPIGateway_TEST"
  action        = "lambda:InvokeFunction"
  function_name = var.function_name_TEST
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_id_TEST}/*/*/*"
}


variable "function_name_TEST" {
    description = "AWS region"
    type        = string
    default     = ""
}


variable "api_gateway_id_TEST" {
    description = "API Gateway ID"
    type        = string
    default     = ""
}
