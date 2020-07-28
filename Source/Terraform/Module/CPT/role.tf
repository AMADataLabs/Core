resource "aws_iam_role" "lambda_role" {
    name = "DataLabsCPTLambdaExecution"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            }
        }
    ]
}
EOF

    tags = merge(local.tags, {Name = "CPT API Lambda function execution role"})
}


resource "aws_iam_policy" "lambda_logging" {
    name        = "DataLabsCPTLambdaLogging"
    path        = "/"
    description = "IAM policy for logging from a lambda"

    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_logs" {
    role       = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.lambda_logging.arn
}


resource "aws_iam_policy" "lambda_kms_access" {
    name        = "DataLabsCPTLambdaKMSAccess"
    path        = "/"
    description = "IAM policy for allowing Lambdas to decrypt SSM secure strings"

    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "kms:DescribeKey",
        "kms:GetKeyPolicy",
        "kms:GetKeyRotationStatus",
        "kms:GetPublicKey",
        "kms:ListKeys",
        "kms:ListAliases",
        "kms:ListKeyPolicies"
      ],
      "Resource": "${data.aws_kms_key.cpt.arn}",
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_kms_access" {
    role       = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.lambda_kms_access.arn
}


resource "aws_iam_policy" "lambda_s3_access" {
    name        = "DataLabsCPTLambdaS3Access"
    path        = "/"
    description = "IAM policy for accessing S3 from a lambda"

    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:ListBucket",
        "s3:ListObjects",
        "s3:ListObjectsV2",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "*",
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
    role       = aws_iam_role.lambda_role.name
    policy_arn = aws_iam_policy.lambda_s3_access.arn
}


data "aws_kms_key" "cpt" {
  key_id = "alias/DataLabs/CPT"
}
