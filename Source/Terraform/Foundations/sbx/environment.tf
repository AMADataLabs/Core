provider "aws" {
    region = "us-east-1"
}


terraform {
    required_version = "= 1.5.3"

    backend "s3" {
        bucket          = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
        key             = "Foundations/sandbox.tfstate"
        region          = "us-east-1"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }

    required_providers {
        aws = {
            version = "= 5.10.0"
        }
    }
}
