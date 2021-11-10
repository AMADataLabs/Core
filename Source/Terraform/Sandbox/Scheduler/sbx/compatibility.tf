#####################################################################
# Sandbox-specific Compatibility Resources                          #
#####################################################################

resource "aws_ecr_repository" "scheduler" {
    name                 = "${lower(var.project)}-${local.environment}"

    tags                    = {
        Name                    = "ECR Repository for Scheduler content ETL and API code"
        Environment             = local.environment
        Contact                 = var.contact
        BudgetCode              = var.budget_code
        Owner                   = var.owner
        ProjectName             = var.project
        SystemTier              = "0"
        DRTier                  = "0"
        DataClassification      = "N/A"
        Notes                   = "N/A"
        OS                      = "N/A"
        EOL                     = "N/A"
        MaintenanceWindow       = "N/A"
        Group                   = "Health Solutions"
        Department              = "DataLabs"
    }
}
