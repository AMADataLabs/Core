provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


terraform {
    backend "s3" {
        bucket          = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
        key             = "Scheduler/sandbox.tfstate"
        region          = "us-east-1"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }
}


data "terraform_remote_state" "infrastructure" {
  backend = "s3"

  config = {
    bucket          = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
    key             = "DataLake/sandbox.tfstate"
    region          = "us-east-1"
    dynamodb_table  = "hsg-datalabs-terraform-locks"
  }
}
