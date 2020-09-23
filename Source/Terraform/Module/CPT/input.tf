variable "project" {
    description     = "Project name used in tags and names to distinguish resources."
    type            = string
}

variable "rds_instance_name" {
    description = "RDS instance identifier"
    type        = string
    default     = "datalabs-api-backend"
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


variable "database_name" {
    description = "database name"
    type        = string
    default     = "cpt-api"
}


variable "passport_url" {
    description = "Passport Url"
    type        = string
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


data "aws_ssm_parameter" "database_username" {
    name = "/DataLabs/${var.project}/RDS/username"
}


data "aws_ssm_parameter" "database_password" {
    name = "/DataLabs/${var.project}/RDS/password"
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


data "aws_ssm_parameter" "ingestion_bucket" {
    name = "/DataLabs/DataLake/ingestion_bucket"
}


data "aws_ssm_parameter" "processed_bucket" {
    name = "/DataLabs/DataLake/processed_bucket"
}


data "aws_kms_key" "cpt" {
  key_id = "alias/DataLabs/${var.project}"
}


data "aws_sns_topic" "ingestion" {
    name = "IngestionBucketNotification"
}


data "aws_sns_topic" "processed" {
    name = "ProcessedBucketNotification"
}
