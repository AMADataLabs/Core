locals {
    environment 			= "sbx"
	account                 = lookup(var.accounts, local.environment)
	ecr_account				= local.account

    department          = "HS"
    group               = "DataLabs"

    function_names = {
        scheduler                   = "${var.project}-${local.environment}-Scheduler"
        dag_processor               = "${var.project}-${local.environment}-DAGProcessor"
        task_processor              = "${var.project}-${local.environment}-TaskProcessor"
    }

    topic_names = {
      ingested_data               = "${var.project}-${local.environment}-ingested-data"
      processed_data              = "${var.project}-${local.environment}-processed-data"
      scheduler                   = "${var.project}-${local.environment}-Scheduler"
      dag_processor               = "${var.project}-${local.environment}-DAGProcessor"
      task_processor              = "${var.project}-${local.environment}-TaskProcessor"
    }

    runtime = "python3.7"
    region = "us-east-1"

    tags                = {
        Environment         = local.environment
        Contact             = var.contact
        SystemTier          = "0"
        DRTier              = "0"
        DataClassification  = "N/A"
        BudgetCode          = var.budget_code
        Owner               = var.owner
        ProjectName         = var.project
        Notes               = "N/A"
        OS                  = "N/A"
        EOL                 = "N/A"
        MaintenanceWindow   = "N/A"
        Group               = local.group
        Department          = local.department
    }

    ### replicate TE stacks ##
    subnets = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
    host_suffix = lookup(var.host_suffixes, local.environment)
    datanow_domain      = "${var.datanow_host_prefix}${local.host_suffix}.${var.domain}"

    parameter_name_prefix = "/${var.project}/${local.environment}/"
}
