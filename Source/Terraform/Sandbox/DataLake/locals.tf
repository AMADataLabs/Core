locals {
    budget_code         = "PBW"
    contact             = "DataLabs@ama-assn.org"
    department          = "HS"
    group               = "DataLabs"
    na                  = "N/A"
    owner               = "DataLabs"
    project             = "DataLake"
    tier                = "0"

    function_names = {
        scheduler                   = "${var.project}-${var.environment}-Scheduler"
        dag_processor               = "${var.project}-${var.environment}-DAGProcessor"
        task_processor              = "${var.project}-${var.environment}-TaskProcessor"
    }

    topic_names = {
      ingested_data               = "${var.project}-${var.environment}-ingested-data"
      processed_data              = "${var.project}-${var.environment}-processed-data"
      scheduler                   = "${var.project}-${var.environment}-Scheduler"
      dag_processor               = "${var.project}-${var.environment}-DAGProcessor"
      task_processor              = "${var.project}-${var.environment}-TaskProcessor"
    }

    runtime = "python3.7"
    region = "us-east-1"

    tags                = {
        Environment         = var.environment
        Contact             = local.contact
        SystemTier          = local.tier
        DRTier              = local.tier
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        ProjectName         = var.project
        Notes               = "N/A"
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
        Group               = local.group
        Department          = local.department
    }

    ### replicate TE stacks ##
    environment = var.environment
    subnets = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
    host_suffix = lookup(var.host_suffixes, local.environment)
    datanow_domain      = "${var.datanow_host_prefix}${local.host_suffix}.${var.domain}"

    parameter_name_prefix = "/${var.project}/${local.environment}/"
}
