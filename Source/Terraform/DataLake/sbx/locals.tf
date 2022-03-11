locals {
    environment 			= "sbx"
	account                 = lookup(var.accounts, local.environment)
	ecr_account				= local.account

    datanow_image           = "${var.datanow_image_prefix}-${local.environment}"
    s3_lambda_bucket        = "ama-${local.environment}-datalake-${var.s3_lambda_bucket_base_name}-us-east-1"

	host_suffix 			= lookup(var.host_suffixes, local.environment)
	datanow_domain      	= "${var.datanow_host_prefix}${local.host_suffix}.${var.domain}"

	parameter_name_prefix 	= "/${var.project}/${local.environment}/"

    lambda_names = {
        scheduler       = "${var.project}-${local.environment}-Scheduler"
        dag_processor   = "${var.project}-${local.environment}-DAGProcessor"
        task_processor  = "${var.project}-${local.environment}-TaskProcessor"
    }

    topic_names = {
      ingested_data     = "${var.project}-${local.environment}-ingested-data"
      processed_data    = "${var.project}-${local.environment}-processed-data"
      scheduler         = "${var.project}-${local.environment}-Scheduler"
      dag_processor     = "${var.project}-${local.environment}-DAGProcessor"
      task_processor    = "${var.project}-${local.environment}-TaskProcessor"
    }

    department          = "HS"
    group               = "DataLabs"
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
    subnets = ["subnet-020fca7291c7d0074", "subnet-0962128cae1b4816d"]
}
