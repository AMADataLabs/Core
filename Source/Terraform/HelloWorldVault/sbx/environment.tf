provider "aws" {
  region  = "us-east-1"
  version = ">= 4.12.1"
}


terraform {
  backend "s3" {
    bucket         = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
    key            = "HelloWorldVault/sbx.tfstate"
    region         = "us-east-1"
    dynamodb_table = "hsg-datalabs-terraform-locks"
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
