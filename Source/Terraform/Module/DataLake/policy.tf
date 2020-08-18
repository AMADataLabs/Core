resource "aws_s3_bucket_policy" "datalake_ingestion_bucket" {
  bucket = aws_s3_bucket.datalake_ingestion_bucket.id

  policy = <<POLICY
{
    "Id": "S3-Console-Replication-Policy",
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3PolicyStmt-DO-NOT-MODIFY-1597230941297",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::655665223663:root"
            },
            "Action": [
                "s3:GetBucketVersioning",
                "s3:PutBucketVersioning",
                "s3:ReplicateObject",
                "s3:ReplicateDelete",
                "s3:ObjectOwnerOverrideToBucketOwner"
            ],
            "Resource": [
                "${aws_s3_bucket.datalake_ingestion_bucket.arn}/IVL/HospitalGroupAffiliation/*"
            ]
        }
    ]
}
POLICY
}



