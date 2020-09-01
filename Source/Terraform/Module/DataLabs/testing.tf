resource "aws_iam_role" "codebuild" {
    name = "codebuild-HSGDataLabsTest-service-role"
    path = "/service-role/"

    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

    tags = merge(local.tags, {Name = "Data Labs CodeBuild policy"})
}


resource "aws_iam_role_policy" "codebuild" {
    role = aws_iam_role.codebuild.name

    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:logs:${local.region}:${data.aws_caller_identity.account.account_id}:log-group:DataLabs",
                "arn:aws:logs:${local.region}:${data.aws_caller_identity.account.account_id}:log-group:DataLabs:*"
            ],
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ]
        },
        {
            "Effect": "Allow",
            "Resource": [
                "arn:aws:s3:::codepipeline-${local.region}-*"
            ],
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:GetBucketAcl",
                "s3:GetBucketLocation"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "codebuild:CreateReportGroup",
                "codebuild:CreateReport",
                "codebuild:UpdateReport",
                "codebuild:BatchPutTestCases",
                "codebuild:BatchPutCodeCoverages"
            ],
            "Resource": [
                "arn:aws:codebuild:${local.region}:${data.aws_caller_identity.account.account_id}:report-group/HSGDataLabsTest-*"
            ]
        }
    ]
}
EOF
}
