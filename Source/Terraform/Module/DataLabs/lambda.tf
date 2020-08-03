
resource "aws_s3_bucket" "datalabs_lambda_code_bucket" {
    bucket = data.aws_ssm_parameter.lambda_code_bucket.value

    lifecycle {
        prevent_destroy = true
    }

    tags = merge(local.tags, {Name = "Data Labs Lambda Code Bucket"})
}


resource "aws_s3_bucket_public_access_block" "datalabs_lambda_code_bucket_public_access_block" {
    bucket = data.aws_ssm_parameter.lambda_code_bucket.value

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

    depends_on = [aws_s3_bucket.datalabs_lambda_code_bucket]
}
