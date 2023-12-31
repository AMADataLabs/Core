provider "aws" {
  region  = "us-east-1"
  version = "~> 3.0"
}


terraform {
  backend "s3" {
    bucket         = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
    key            = "Legacy/sandbox.tfstate"
    region         = "us-east-1"
    dynamodb_table = "hsg-datalabs-terraform-locks"
  }

  required_providers {
    aws = "3.74.3"
  }
}


data "terraform_remote_state" "infrastructure" {
  backend = "s3"

  config = {
    bucket         = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
    key            = "Foundations/sandbox.tfstate"
    region         = "us-east-1"
    dynamodb_table = "hsg-datalabs-terraform-locks"
  }
}
