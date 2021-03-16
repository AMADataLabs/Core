variable "project" {
    description     = "Project name used in tags and names to distinguish resources."
    type            = string
}


variable "rds_instance_class" {
    description = "RDS instance class"
    type        = string
    default     = "db.t2.micro"
}


variable "rds_storage_type" {
    description = "RDS storage type"
    type        = string
    default     = "gp2"
}


variable "endpoint_timeout" {
    description = "timeout in seconds"
    type        = number
    default     = 15
}


variable "endpoint_memory_size" {
    description = "memory size in Mb"
    type        = number
    default     = 1024
}


data "aws_caller_identity" "account" {}


data "aws_secretsmanager_secret" "database" {
  name = "DataLabs/${var.project}/API/database"
}

data "aws_secretsmanager_secret_version" "database" {
  secret_id = data.aws_secretsmanager_secret.database.id
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "s3_base_path" {
    name  = "/DataLabs/${var.project}/s3/base_path"
}


data "aws_ssm_parameter" "raw_data_files" {
    name  = "/DataLabs/${var.project}/data/raw_files"
}


data "aws_ssm_parameter" "release_schedule" {
    name  = "/DataLabs/${var.project}/release/schedule"
}


data "aws_ssm_parameter" "raw_data_parsers" {
    name  = "/DataLabs/${var.project}/data/parsers"
}


data "aws_ssm_parameter" "converted_data_files" {
    name  = "/DataLabs/${var.project}/data/converted_files"
}

data "aws_ssm_parameter" "raw_csv_files" {
    name  = "/DataLabs/${var.project}/data/raw_csv_files"
}


data "aws_ssm_parameter" "pdf_files" {
    name  = "/DataLabs/${var.project}/data/pdf_files"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "ingested_data_bucket" {
    name = "/DataLabs/DataLake/ingested_data_bucket"
}


data "aws_ssm_parameter" "processed_data_bucket" {
    name = "/DataLabs/DataLake/processed_data_bucket"
}


data "aws_kms_key" "cpt" {
  key_id = "alias/DataLabs/${var.project}"
}


data "aws_sns_topic" "ingested_data" {
    name = "IngestedDataBucketNotification"
}


data "aws_sns_topic" "processed_data" {
    name = "ProcessedDataBucketNotification"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}


data "aws_ssm_parameter" "passport_url" {
    name  = "/DataLabs/${var.project}/auth/passport_url"
}
