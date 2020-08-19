resource "aws_lambda_permission" "child_function" {
    statement_id  = "AllowExecutionFromParentLambda"
    action        = "lambda:InvokeFunction"
    function_name = var.function_name
    principal     = "s3.amazonaws.com"
    source_arn    = var.parent_function.arn

    depends_on = [aws_lambda_function.etl_lambda]
}
