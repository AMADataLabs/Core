provider "aws" {
    region = "us-east-1"
}

resource "aws_s3_bucket" "datalake_ingestion_bucket" {
    acl = "private"
    force_destroy = false

    tags = {
        Name = "Data Labs Data Lake Ingestion Bucket"
        Env                 = var.environment
        Contact             = var.contact
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


variable "environment" {
    description = "AWS Account Environment"
    type        = string
    default     = "Sandbox"
}


variable "contact" {
    description = "Email address of the Data Labs contact."
    type        = string
    default     = "DataLabs@ama-assn.org"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = "Experimental"
}