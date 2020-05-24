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
    type  = "String"
    value = var.password
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_LAMBDA_FUNCTION" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_LAMBDA_FUNCTION"
    type  = "String"
    value = "ConvertCPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_APP" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_APP"
    type  = "String"
    value = "datalabs.etl.run.lambda_handler"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR"
    type  = "String"
    value = "datalabs.etl.s3.extract.S3Extractor"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR_BUCKET" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR_BUCKET"
    type  = "String"
    value = data.aws_ssm_parameter.ingestion_bucket.value
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR_BASE_PATH" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR_BASE_PATH"
    type  = "String"
    value = "AMA/CPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR_FILES" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR_FILES"
    type  = "String"
    value = "standard/SHORTU.txt,standard/MEDU.txt,standard/LONGULT.txt,standard/MODUL.txt,standard/Clinician Descriptors/ClinicianDescriptor.txt"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_TRANSFORMER" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_TRANSFORMER"
    type  = "String"
    value = "datalabs.etl.cpt.transform.CPTFileToCSVTransformer"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_TRANSFORMER_PARSERS" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_TRANSFORMER_PARSERS"
    type  = "String"
    value = "datalabs.curate.cpt.descriptor.ShortDescriptorParser,datalabs.curate.cpt.descriptor.MediumDescriptorParser,datalabs.curate.cpt.descriptor.LongDescriptorParser,datalabs.curate.cpt.modifier.ModifierParser,datalabs.curate.cpt.descriptor.ClinicianDescriptorParser,datalabs.curate.cpt.descriptor.ConsumerDescriptorParser"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER"
    type  = "String"
    value = "datalabs.etl.s3.load.S3Loader"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER_BUCKET" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER_BUCKET"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-processed-sandbox"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER_FILES" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER_FILES"
    type  = "String"
    value = "standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER_BASE_PATH" {
    name  = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER_BASE_PATH"
    type  = "String"
    value = "AMA/CPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_LAMBDA_FUNCTION" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_LAMBDA_FUNCTION"
    type  = "String"
    value = "LoadCPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_APP" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_APP"
    type  = "String"
    value = "datalabs.etl.ETL"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR"
    type  = "String"
    value = "datalabs.etl.s3.extract.S3Extractor"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR_BUCKET" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR_BUCKET"
    type  = "String"
    value = data.aws_ssm_parameter.processed_bucket.value
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR_BASE_PATH" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR_BASE_PATH"
    type  = "String"
    value = "AMA/CPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR_FILES" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR_FILES"
    type  = "String"
    value = "standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_TRANSFORMER" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_TRANSFORMER"
    type  = "String"
    value = "datalabs.etl.transform.PassThroughTransformer"
    tags = local.tags
}


resource "aws_ssm_parameter" "ETL_LOADCPT_LOADER" {
    name  = "/DataLabs/CPT/ETL_LOADCPT_LOADER"
    type  = "String"
    value = "datalabs.etl.cpt.load.load.RDSLoader"
    tags = local.tags
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/DataLake/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/DataLake/contact"
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
