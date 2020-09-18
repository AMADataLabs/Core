provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


resource "aws_ssm_parameter" "ingestion_bucket" {
    name  = "/DataLabs/${local.project}/ingestion_bucket"
    type  = "String"
    value = format("ama-hsg-datalabs-%s-ingestion-sandbox", lower(local.project))
    tags = local.tags
}


resource "aws_ssm_parameter" "processed_bucket" {
    name  = "/DataLabs/${local.project}/processed_bucket"
    type  = "String"
    value = format("ama-hsg-datalabs-%s-processed-sandbox", lower(local.project))
    tags = local.tags
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
