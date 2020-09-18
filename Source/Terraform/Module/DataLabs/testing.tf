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


resource "aws_codebuild_source_credential" "codebuild" {
  auth_type   = "BASIC_AUTH"
  server_type = "BITBUCKET"
  user_name   = var.bitbucket_username
  token       = var.bitbucket_app_password
}


resource "aws_codebuild_project" "testing" {
    name = "HSGDataLabsTest"
    service_role = aws_iam_role.codebuild.arn

    source {
      type              = "BITBUCKET"
      location          = "https://hsgdatalabs@bitbucket.org/hsdatalabs/hsg-data-labs.git"
      buildspec         = "Build/Master/buildspec.yaml"
      git_clone_depth = 1

      auth {
          type          = "OAUTH"
          resource      = aws_codebuild_source_credential.codebuild.arn
      }
    }

    environment {
        compute_type                = "BUILD_GENERAL1_MEDIUM"
        image                       = "aws/codebuild/standard:4.0"
        type                        = "LINUX_CONTAINER"
        image_pull_credentials_type = "CODEBUILD"
    }

    artifacts {
      type = "NO_ARTIFACTS"
    }

    logs_config {
        cloudwatch_logs {
            group_name  = var.project
            status      = "ENABLED"
            stream_name = "Test"
        }

        s3_logs {
            status              = "DISABLED"
            encryption_disabled = false
        }
    }

    tags = merge(local.tags, {Name = "Data Labs CodeBuild testing project"})
}
