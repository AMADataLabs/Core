provider "aws" {
    region = "us-east-1"
}


resource "aws_s3_bucket" "datalake_ingestion_bucket" {
    bucket = data.aws_ssm_parameter.ingestion_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    tags = merge(local.tags, {Name = "Data Labs Data Lake Ingestion Bucket"})
}


resource "aws_s3_bucket" "datalake_processed_bucket" {
    bucket = data.aws_ssm_parameter.processed_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    tags = merge(local.tags, {Name = "Data Labs Data Lake Processed Bucket"})
}


resource "aws_s3_bucket_public_access_block" "datalake_ingestion_bucket_public_access_block" {
    bucket = data.aws_ssm_parameter.ingestion_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}


resource "aws_s3_bucket_public_access_block" "datalake_processed_bucket_public_access_block" {
    bucket = data.aws_ssm_parameter.processed_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
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


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = ""
    tags = {
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
