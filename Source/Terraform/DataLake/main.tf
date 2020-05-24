provider "aws" {
    region = "us-east-1"
}


resource "aws_s3_bucket" "datalake_ingestion_bucket" {
    bucket = data.aws_ssm_parameter.ingestion_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    tags = {
        Name = "Data Labs Data Lake Ingestion Bucket"
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


resource "aws_s3_bucket" "datalake_processed_bucket" {
    bucket = data.aws_ssm_parameter.processed_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    tags = {
        Name = "Data Labs Data Lake Processed Bucket"
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


# variable "environment" {
#     description = "AWS Account Environment"
#     type        = string
#     default     = "Sandbox"
# }


# variable "contact" {
#     description = "Email address of the Data Labs contact."
#     type        = string
#     default     = "DataLabs@ama-assn.org"
# }


locals {
    # ingestion_bucket    = format("ama-hsg-datalabs-datalake-ingestion-%s", lower(var.environment))
    # processed_bucket    = format("ama-hsg-datalabs-datalake-processed-%s", lower(var.environment))
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = ""
}
