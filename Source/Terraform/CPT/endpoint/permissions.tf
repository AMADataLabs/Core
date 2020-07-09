resource "aws_lambda_permission" "lambda_permissions" {
    statement_id  = "AllowExecutionFromAPIGateway"
    action        = "lambda:InvokeFunction"
    function_name = var.function_name
    principal     = "apigateway.amazonaws.com"
    source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_id}/*/*/*"

    depends_on = [aws_lambda_function.endpoint_lambda]
}



resource "aws_lambda_permission" "lambda_permissions_TEST" {
    count = var.function_name_TEST == "" ? 0 : 1

    statement_id  = "AllowExecutionFromAPIGateway_TEST"
    action        = "lambda:InvokeFunction"
    function_name = var.function_name_TEST
    principal     = "apigateway.amazonaws.com"
    source_arn    = "arn:aws:execute-api:${var.region}:${var.account_id}:${var.api_gateway_id_TEST}/*/*/*"

    depends_on = [aws_lambda_function.endpoint_lambda]
}
