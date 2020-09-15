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


variable "api_gateway_id" {
    description = "API Gateway ID"
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


variable "s3_base_path" {
    description = "Base path for CPT data in S3"
    type        = string
}
