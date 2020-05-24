resource "aws_ssm_parameter" "account_environment" {
  name  = "/DataLabs/DataLake/account_environment"
  type  = "String"
  value = "Sandbox"
}


resource "aws_ssm_parameter" "contact" {
  name  = "/DataLabs/DataLake/contact"
  type  = "String"
  value = "DataLabs@ama-assn.org"
}


resource "aws_ssm_parameter" "ingestion_bucket_name" {
  name  = "/DataLabs/DataLake/ingestion_bucket"
  type  = "String"
  value = "ama-hsg-datalabs-datalake-ingestion-sandbox"
}


resource "aws_ssm_parameter" "processed_bucket_name" {
  name  = "/DataLabs/DataLake/processed_bucket"
  type  = "String"
  value = "ama-hsg-datalabs-datalake-processed-sandbox"
}

