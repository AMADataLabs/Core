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
