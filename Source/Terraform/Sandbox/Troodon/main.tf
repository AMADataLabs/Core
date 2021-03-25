provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}

terraform {
    backend "s3" {
        bucket          = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
        key             = "Troodon/sandbox.tfstate"
        region          = "us-east-1"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }
}


resource "aws_codebuild_project" "troodon" {
    name          = "CodeBuildProject-GskTYS0yOv1X"
    service_role  = "arn:aws:iam::644454719059:role/SC-644454719059-pp-iho6z7zkmlz22-CodeBuildRole-1TC3J9IPK4TAQ"
    build_timeout = 20

    environment {
        image = "644454719059.dkr.ecr.us-east-1.amazonaws.com/cbtroodon"
        compute_type = "BUILD_GENERAL1_SMALL"
        type = "LINUX_CONTAINER"
    }

    source {
        type = "S3"
        location = "troodonstaging20150646/infraspec.zip"
    }

    artifacts {
        type = "S3"
        location = "troodonstaging20150646"
        name = "infraspec.zip"
        namespace_type = "BUILD_ID"
        packaging = "NONE"
        path = "terraformbuilds"
    }
}


resource "aws_iam_role" "troodon" {
    name = "SC-644454719059-pp-iho6z7zkmlz22-CodeBuildRole-1TC3J9IPK4TAQ"

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
}


resource "aws_iam_role_policy" "troodon" {
    role = aws_iam_role.example.troodon

    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Resource": [
        "*"
      ],
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterface",
        "ec2:DescribeDhcpOptions",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeVpcs"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateNetworkInterfacePermission"
      ],
      "Resource": [
        "arn:aws:ec2:us-east-1:123456789012:network-interface/*"
      ],
      "Condition": {
        "StringEquals": {
          "ec2:Subnet": [
            "${aws_subnet.example1.arn}",
            "${aws_subnet.example2.arn}"
          ],
          "ec2:AuthorizedService": "codebuild.amazonaws.com"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "${aws_s3_bucket.example.arn}",
        "${aws_s3_bucket.example.arn}/*"
      ]
    }
  ]
}
POLICY
}
