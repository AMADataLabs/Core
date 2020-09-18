provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


module "datalabs_terraform_state" {
    source  = "../../Module/DataLake"
    project = "DataLake"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    notes               = ""
    project             = "DataLake"
    tags                = {
        Name = "Data Labs Data Lake Parameter"
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        Project             = local.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
