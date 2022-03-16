resource "aws_batch_compute_environment" "compute_environment" {
  compute_environment_name = "ecs-scheduler-env"

  compute_resources {
    max_vcpus = 2

    security_group_ids = security_groups

    #NOTE: HADI, are you sure? ask Peter
    subnets = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    # subnets = ["subnet-0a508711165923924"]
    # subnets = ["arn:aws:ec2:us-east-1:644454719059:subnet/subnet-0a508711165923924"]

    type = "FARGATE"
  }

  service_role = aws_iam_role.scheduler_batch_service_role.arn
  # service_role = "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role"
  type       = "MANAGED"
  depends_on = [aws_iam_role_policy_attachment.aws_batch_service_role]

  tags = {
    Name               = "${var.project}-${local.environment}-ecs-scheduler-env"
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
