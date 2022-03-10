provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


terraform {
    backend "s3" {
        bucket          = "ama-ivl-foundations-terraform-state"
        key             = "Foundations/ivl.tfstate"
        region          = "us-east-1"
        dynamodb_table  = "ama-ivl-foundations-terraform-locks"
    }

    required_providers {
        aws = "3.37"
    }
}
