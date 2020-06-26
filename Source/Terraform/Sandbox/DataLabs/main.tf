provider "aws" {
    region = "us-east-1"
}


resource "aws_ssm_parameter" "account_environment" {
    name  = "/DataLabs/account_environment"
    type  = "String"
    value = local.account_environment
    tags = local.tags
}


resource "aws_ssm_parameter" "contact" {
    name  = "/DataLabs/contact"
    type  = "String"
    value = local.Contact
    tags = local.tags
}


locals {
    account_environment = "Sandbox"
    contact             = "DataLabs@ama-assn.org"
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = ""
    tags                = {
        Name = "Data Labs Data Lake Parameter"
        Env                 = "Sandbox"
        Contact             = local.contact
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
