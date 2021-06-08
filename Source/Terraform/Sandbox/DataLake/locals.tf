locals {
    budget_code         = "PBW"
    contact             = "DataLabs@ama-assn.org"
    department          = "HS"
    group               = "DataLabs"
    na                  = "N/A"
    owner               = "DataLabs"
    project             = "DataLake"
    tier                = "0"
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
    function_names = {
        scheduler                   = "${var.project}-Scheduler-${var.environment}"
        dag_processor               = "${var.project}-DAG-Processor-${var.environment}"
        task_processor              = "${var.project}-Task-Processor-${var.environment}"
    }
    topic_names = {
      scheduler                   = "${var.project}-Scheduler-${var.environment}"
      dag_processor               = "${var.project}-DAG-Processor-${var.environment}"
      task_processor              = "${var.project}-Task-Processor-${var.environment}"
    }
    runtime = "python3.7"
    region = "us-east-1"
}
