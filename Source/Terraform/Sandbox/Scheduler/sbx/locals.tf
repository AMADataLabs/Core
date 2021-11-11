locals {
    environment               = regex("(?:.+/)(?P<environment>..*)", abspath(path.root)).environment
    account                   = lookup(var.accounts, local.environment)
    ecr_account               = local.environment == "sbx" ? local.account : "394406051370"

    subs                      = {
      environment       = local.environment
      account           = local.account
      ecr_account       = local.ecr_account
    }
    scheduler_image             = join("", [for word in split("%%", var.scheduler_image_template): lookup(local.subs, word, word)])

    tags                = {
        Name                = "Data Labs ${var.project} Parameter"
        Environment         = local.environment
        Contact             = var.contact
        SystemTier          = "0"
        DRTier              = "0"
        DataClassification  = "N/A"
        BudgetCode          = var.budget_code
        Owner               = var.owner
        Group               = var.owner
        Department          = "HS"
        ProjectName         = var.project
        OS                  = "N/A"
        EOL                 = "N/A"
        MaintenanceWindow   = "N/A"
    }
}
