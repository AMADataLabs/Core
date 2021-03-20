provider "aws" {
    region = "us-east-1"
}


resource "aws_ssm_parameter" "account_environment" {
    name  = "/DataLabs/DataLake/account_environment"
    type  = "String"
    value = "Production"

    tags = {
        Name = "Data Labs Data Lake Paramter"
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Notes               = local.notes
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}


resource "aws_ssm_parameter" "contact" {
    name  = "/DataLabs/contact"
    type  = "String"
    value = "DLHSDataLabs@ama-assn.org"
}


resource "aws_ssm_parameter" "ingested_data_bucket" {
    name  = "/DataLabs/DataLake/ingested_data_bucket"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-ingestion"
}


resource "aws_ssm_parameter" "processed_data_bucket" {
    name  = "/DataLabs/DataLake/processed_data_bucket"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-processed"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
}
