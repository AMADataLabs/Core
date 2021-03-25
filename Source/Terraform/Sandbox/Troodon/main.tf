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
