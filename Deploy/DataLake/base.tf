provider "aws" {
    region = "us-east-2"
}

resource "aws_s3_bucket" "terraform_state" {
    bucket = "ama-hsg-datalabs-datalake-terraform-state-sandbox"

    lifecycle {
        prevent_destroy = true
    }

    versioning {
        enabled = true
    }

    tags = {
        Name = "Data Labs Datalake Terraform State Bucket"
        Env                 = "Sandbox"
        Contact             = peter.lane@ama-assn.org
        SystemTier          = "Application"
        DRTier              = "N/A"
        DataClassification  = "N/A"
        BudgetCode          = "PBW"
        Owner               = "Data Labs"
        Notes               = "Experimental"
        OS                  = "N/A"
        EOL                 = "N/A"
        MaintenanceWindow   = "N/A"
    }
}


resource "aws_dynamodb_table" "terraform_locks" {
    name            = "hsg-datalabs-terraform-locks"
    billing_mode    = "PAY_PER_REQUEST"
    hash_key        = "LockID"

    attribute {
        name = "LockID"
        type = "S"
    }

    tags = {
        Name = "Data Labs Datalake Terraform State Bucket"
        Env                 = "Sandbox"
        Contact             = peter.lane@ama-assn.org
        SystemTier          = "Application"
        DRTier              = "N/A"
        DataClassification  = "N/A"
        BudgetCode          = "PBW"
        Owner               = "Data Labs"
        Notes               = "Experimental"
        OS                  = "N/A"
        EOL                 = "N/A"
        MaintenanceWindow   = "N/A"
    }
}

terraform {
    backend "s3" {
        bucket          = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
        key             = "global/s3/base.tfstate"
        region          = "us-east-2"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }
}
