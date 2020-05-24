provider "aws" {
    region = "us-east-1"
}


resource "aws_ssm_parameter" "account_environment" {
  name  = "/DataLabs/DataLake/account_environment"
  type  = "String"
  value = "Production"
}


resource "aws_ssm_parameter" "contact" {
  name  = "/DataLabs/DataLake/contact"
  type  = "String"
  value = "DLHSDataLabs@ama-assn.org"
}


resource "aws_ssm_parameter" "ingestion_bucket" {
  name  = "/DataLabs/DataLake/ingestion_bucket"
  type  = "String"
  value = "ama-hsg-datalabs-datalake-ingestion"
}


resource "aws_ssm_parameter" "processed_bucket" {
  name  = "/DataLabs/DataLake/processed_bucket"
  type  = "String"
  value = "ama-hsg-datalabs-datalake-processed"
}

