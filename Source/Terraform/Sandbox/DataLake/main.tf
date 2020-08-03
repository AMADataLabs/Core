provider "aws" {
    region = "us-east-1"
}


module "datalabs_terraform_state" {
    source = "../../Module/DataLake"
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    notes               = ""
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
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
