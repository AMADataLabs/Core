resource "aws_s3_bucket" "terraform_state_store" {
    bucket = "ama-hsg-datalabs-datalake-terraform-state-sandbox"

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


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = "Experimental"
}