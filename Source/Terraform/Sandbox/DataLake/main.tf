provider "aws" {
    region = "us-east-1"
}


resource "aws_ssm_parameter" "account_environment" {
    name  = "/DataLabs/DataLake/account_environment"
    type  = "String"
    value = "Sandbox"
    tags = local.tags
}


resource "aws_ssm_parameter" "contact" {
    name  = "/DataLabs/DataLake/contact"
    type  = "String"
    value = "DLHSDataLabs@ama-assn.org"
    tags = local.tags
}


resource "aws_ssm_parameter" "ingestion_bucket" {
    name  = "/DataLabs/DataLake/ingestion_bucket"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-ingestion-sandbox"
    tags = local.tags
}


resource "aws_ssm_parameter" "processed_bucket" {
    name  = "/DataLabs/DataLake/processed_bucket"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-processed-sandbox"
    tags = local.tags
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/DataLake/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/DataLake/contact"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
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
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
