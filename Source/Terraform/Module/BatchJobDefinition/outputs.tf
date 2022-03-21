output "service_role" {
    value = aws_iam_role.service_role.name
}

output "job_role" {
    value = aws_iam_role.job_role.name
}
