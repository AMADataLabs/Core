output "service_role" {
  value = aws_iam_role.service_role
}

output "arn" {
    value = aws_batch_compute_environment.compute_environment.arn
}
