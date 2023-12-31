provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


module "datalabs_terraform_state" {
    source                      = "../../Module/DataLabs"
    project                     = "DataLabs"
}


locals {
    account_environment = "Sandbox"
    contact             = "DataLabs@ama-assn.org"
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    notes               = ""
    project             = "DataLabs"
    tags                = {
        Name = "Data Labs Data Lake Parameter"
        Env                 = "Sandbox"
        Contact             = local.contact
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        ProjectName         = local.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
