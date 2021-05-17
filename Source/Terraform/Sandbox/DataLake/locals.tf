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
}
