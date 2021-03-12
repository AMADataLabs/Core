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


variable "parent_function" {
    description = "Reference to the Lambda function allowed to invoke ETLs"
}


variable "region" {
    description = "AWS region"
    type        = string
    default     = "us-east-1"
}


variable "timeout" {
    description = "Timeout in seconds for Lambda functions"
    type        = number
    default     = 30
}


variable "memory_size" {
    description = "lambda function memory size in Mb"
    type        = number
    default     = 1024
}


data "aws_kms_key" "cpt" {
  key_id = "alias/DataLabs/${var.project}"
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
