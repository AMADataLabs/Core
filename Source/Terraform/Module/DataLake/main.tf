resource "aws_s3_bucket" "datalake_ingestion_bucket" {
    bucket = data.aws_ssm_parameter.ingested_data_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    versioning {
        enabled = true
    }

    tags = merge(local.tags, {Name = "Data Labs Data Lake Ingested Data Bucket"})
}


resource "aws_s3_bucket" "datalake_processed_bucket" {
    bucket = data.aws_ssm_parameter.processed_data_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    tags = merge(local.tags, {Name = "Data Labs Data Lake Processed Bucket"})
}


resource "aws_s3_bucket_public_access_block" "datalake_ingestion_bucket_public_access_block" {
    bucket = data.aws_ssm_parameter.ingested_data_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

    depends_on = [aws_s3_bucket.datalake_ingestion_bucket]
}


resource "aws_s3_bucket_public_access_block" "datalake_processed_bucket_public_access_block" {
    bucket = data.aws_ssm_parameter.processed_data_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

    depends_on = [aws_s3_bucket.datalake_processed_bucket]
}
