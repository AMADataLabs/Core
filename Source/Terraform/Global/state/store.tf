

resource "aws_s3_bucket" "terraform_state_store" {
    bucket = data.aws_ssm_parameter.terraform_state_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    versioning {
        enabled = true
    }

    tags = merge(local.tags, {Name = "Data Labs Terraform State Bucket"})
}


resource "aws_s3_bucket_public_access_block" "terraform_state_store_public_access_block" {
    bucket = data.aws_ssm_parameter.terraform_state_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}


resource "aws_dynamodb_table" "terraform_locks_store" {
    name            = data.aws_ssm_parameter.terraform_locks_database.value
    billing_mode    = "PAY_PER_REQUEST"
    hash_key        = "LockID"

    attribute {
        name = "LockID"
        type = "S"
    }

    tags = merge(local.tags, {Name = "Data Labs Terraform State Locks Database"})
}


data "aws_ssm_parameter" "terraform_state_bucket" {
    name = "/DataLabs/Terraform/state_bucket"
}


data "aws_ssm_parameter" "terraform_locks_database" {
    name = "/DataLabs/Terraform/locks_database"
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = ""
    tags                = {
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
