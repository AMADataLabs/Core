resource "aws_s3_bucket" "terraform_state_store" {
    bucket = var.state_bucket

    lifecycle {
        prevent_destroy = true
    }

    versioning {
        enabled = true
    }

    tags = {
        Name = "Data Labs Datalake Terraform State Bucket"
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


resource "aws_s3_bucket_public_access_block" "terraform_state_store_public_access_block" {
    bucket = var.state_bucket

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}


resource "aws_dynamodb_table" "terraform_locks_store" {
    name            = "hsg-datalabs-terraform-locks"
    billing_mode    = "PAY_PER_REQUEST"
    hash_key        = "LockID"

    attribute {
        name = "LockID"
        type = "S"
    }

    tags = {
        Name = "Data Labs Datalake Terraform State Bucket"
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


variable "state_bucket" {
    description = "S3 bucket for storing Terraform state."
}


variable "environment" {
    description = "AWS Account Environment"
    type        = string
}


variable "contact" {
    description = "Email address of the Data Labs contact."
    type        = string
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = "Experimental"
}
