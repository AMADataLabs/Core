variable "project" {
    description     = "Project name used in tags and names to distinguish resources."
    type            = string
}

data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "ingestion_bucket" {
    name = "/DataLabs/${var.project}/ingestion_bucket"
}


data "aws_ssm_parameter" "processed_bucket" {
    name = "/DataLabs/${var.project}/processed_bucket"
}


data "aws_caller_identity" "account" {}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    tags = {
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        Project             = var.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
