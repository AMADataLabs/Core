provider "aws" {
    region = "us-east-1"
}


resource "aws_ssm_parameter" "database_username" {
    name  = "/DataLabs/CPT/RDS/username"
    type  = "String"
    value = "DataLabs_UI"
    tags = local.tags
}


resource "aws_ssm_parameter" "database_password" {
    name  = "/DataLabs/CPT/RDS/password"
    type  = "SecureString"
    value = var.password
    tags = local.tags
}


resource "aws_ssm_parameter" "s3_base_path" {
    name  = "/DataLabs/CPT/s3/base_path"
    type  = "String"
    value = "AMA/CPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_data_files" {
    name  = "/DataLabs/CPT/data/raw_files"
    type  = "String"
    value = "standard/SHORTU.txt,standard/MEDU.txt,standard/LONGULT.txt,standard/MODUL.txt,standard/Consumer Friendly Descriptors/ConsumerDescriptor.txt,standard/Clinician Descriptors/ClinicianDescriptor.txt,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA"
    tags = local.tags
}


resource "aws_ssm_parameter" "release_schedule" {
    name  = "/DataLabs/CPT/release/schedule"
    type  = "String"
    value = "{\"ANNUAL\": [\"1-Sep\", \"1-Jan\"], \"Q1\": [\"1-Jan\", \"1-Apr\"], \"Q2\": [\"1-Apr\", \"1-Jul\"], \"Q3\": [\"1-Jul\", \"1-Oct\"], \"Q4\": [\"1-Oct\", \"1-Jan\"]}"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_data_parsers" {
    name  = "/DataLabs/CPT/data/parsers"
    type  = "String"
    value = "datalabs.curate.parse.CSVParser,datalabs.curate.cpt.descriptor.ShortDescriptorParser,datalabs.curate.cpt.descriptor.MediumDescriptorParser,datalabs.curate.cpt.descriptor.LongDescriptorParser,datalabs.curate.cpt.modifier.ModifierParser,datalabs.curate.cpt.descriptor.ConsumerDescriptorParser,datalabs.curate.cpt.descriptor.ClinicianDescriptorParser,datalabs.curate.cpt.pla.PLAParser"
    tags = local.tags
}


resource "aws_ssm_parameter" "converted_data_files" {
    name  = "/DataLabs/CPT/data/converted_files"
    type  = "String"
    value = "standard/release.csv,standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Consumer Friendly Descriptors/ConsumerDescriptor.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv"
    tags = local.tags
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "ingestion_bucket" {
    name = "/DataLabs/DataLake/ingestion_bucket"
}


data "aws_ssm_parameter" "processed_bucket" {
    name = "/DataLabs/DataLake/processed_bucket"
}


variable "password" {}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = ""
    tags                = {
        Name = "Data Labs CPT Parameter"
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
