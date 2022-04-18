resource "aws_batch_job_queue" "job_queue" {
  name     = "${var.project}-${var.environment}-${var.name}"
  state    = "ENABLED"
  priority = var.priority
  compute_environments = [
    var.compute_environment
  ]

  tags = merge(local.tags, { Name = upper("${var.project}-${var.environment}-${var.name}-jq") })
}
