resource "aws_batch_job_queue" "ecs_scheduler_job_queue" {
  name     = "ecs-scheduler-job-queue"
  state    = "ENABLED"
  priority = 1
  compute_environments = [
    aws_batch_compute_environment.ecs_scheduler_env.arn,
  ]

  tags = {
    Name               = "${var.project}-${local.environment}-ecs-scheduler-job-queue"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}
