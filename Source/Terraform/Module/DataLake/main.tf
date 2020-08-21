resource "aws_s3_bucket" "datalake_ingestion_bucket" {
    bucket = data.aws_ssm_parameter.ingestion_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    versioning {
    enabled = true
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

    depends_on = [aws_s3_bucket.datalake_ingestion_bucket]
}


resource "aws_s3_bucket_public_access_block" "datalake_processed_bucket_public_access_block" {
    bucket = data.aws_ssm_parameter.processed_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

    depends_on = [aws_s3_bucket.datalake_processed_bucket]
}


resource "aws_neptune_cluster" "linage_cluster" {
    cluster_identifier                  = "datalabs-lineage"
    skip_final_snapshot                 = true
    iam_database_authentication_enabled = true
    apply_immediately                   = true
    deletion_protection                 = true

    tags = merge(local.tags, {Name = "Data Labs Data Lake Lineage DB Cluster"})
}

resource "aws_neptune_cluster_instance" "lineage" {
    cluster_identifier = aws_neptune_cluster.linage_cluster.id
    instance_class     = "db.t3.medium"
    apply_immediately  = true

    tags = merge(local.tags, {Name = "Data Labs Data Lake Lineage DB Instance"})
}
