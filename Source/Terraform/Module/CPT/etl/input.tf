variable "project" {
    description     = "Project name used in names to distinguish resources."
    type            = string
}

variable "function_name" {
    description = "AWS region"
    type        = string
}


variable "role" {
    description = "Lambda function role"
    type        = string
}


variable "variables" {
    description = "ETL variables"
    # type        = object(string)
}


variable "account_id" {
    description = "AWS Account ID"
    type        = string
}


variable "database_name" {
    description = "API database name"
    type        = string
}


variable "database_backend" {
    description = "API database backend"
    type        = string
    default     = "postgresql+psycopg2"
}


variable "database_host" {
    description = "API RDS host"
    type        = string
}


variable "data_pipeline_ingestion" {
    description = "Indicates an ingestion-side data pipeline ETL"
    type        = bool
    default     = false
}


variable "data_pipeline_api" {
    description = "Indicates an API-side data pipeline ETL"
    type        = bool
    default     = false
}


variable "trigger_bucket" {
    description = "S3 bucket that will trigger ETL Lambda functions"
    type        = string
}


variable "parent_function" {
    description = "Reference to the Lambda function allowed to invoke ETLs"
}


variable "timeout" {
    description = "Timeout in seconds for Lambda functions"
    type        = number
    default     = 30
}


data "aws_kms_key" "cpt" {
  key_id = "alias/DataLabs/${var.project}"
}


data "aws_ssm_parameter" "database_username" {
    name = "/DataLabs/${var.project}/RDS/username"
}


data "aws_ssm_parameter" "database_password" {
    name = "/DataLabs/${var.project}/RDS/password"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}


data "aws_caller_identity" "account" {}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}
