variable "project" {
    description     = "Project name used in names to distinguish resources."
    type            = string
}

variable "function_name" {
    description = "AWS region"
    type        = string
}


variable "task_class" {
    description = "task class name"
    type        = string
}


variable "region" {
    description = "AWS region"
    type        = string
}


variable "account_id" {
    description = "AWS Account ID"
    type        = string
}


variable "role" {
    description = "Lambda function role"
    type        = string
}


variable "api_gateway_arn" {
    description = "API Gateway ARN"
    type        = string
}


variable "database_host" {
    description = "API RDS host"
    type        = string
}


variable "timeout" {
    description = "timeout in seconds"
    type        = number
    default     = 15
}


variable "memory_size" {
    description = "lambda function memory size in Mb"
    type        = number
    default     = 1024
}


data "aws_kms_key" "cpt" {
    key_id = "alias/DataLabs/${var.project}"
}

data "aws_secretsmanager_secret" "database" {
  name = "DataLabs/${var.project}/API/database"
}


data "aws_ssm_parameter" "processed_data_bucket" {
    name = "/DataLabs/DataLake/processed_data_bucket"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}


data "aws_ssm_parameter" "s3_base_path" {
    name = "/DataLabs/${var.project}/s3/base_path"
}


data "aws_caller_identity" "account" {}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}
