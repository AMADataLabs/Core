output "authorizer_uri" {
  value = aws_lambda_function.authorizer_lambda.invoke_arn
}


output "authorizer_credentials" {
  value = aws_iam_role.invocation_role.arn
}
