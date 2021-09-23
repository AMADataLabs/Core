variable "project" {
    description     = "Name of the project associated with this application stack."
    type            = string
    default         = "DataLake"
}

variable "environment" {
    description     = "Name of the AWS deployment environment."
    type            = string
    default         = "sbx"
}

variable "region" {
    description     = "Name of the AWS deployment region."
    type            = string
    default         = "us-east-1"
}

variable "old_lambda_code_bucket" {
    description     = "Name of the S3 bucket used to hold Lambda function code artifacts."
    type            = string
    default         = "ama-hsg-datalabs-lambda-code-sandbox"
}

variable "lambda_code_bucket" {
    description     = "Name of the S3 bucket used to hold Lambda function code artifacts."
    type            = string
    default         = "ama-sbx-datalake-lambda-us-east-1"
}


variable "scheduler_memory_size" {
    description = "memory size in Mb"
    type        = number
    default     = 1024
}


variable "scheduler_timeout" {
    description = "timeout in seconds"
    type        = number
    default     = 15
}


variable "datanow_image" {
    description     = "ECR repository (image name) for the DataNow container image."
    type            = string
    default         = "datanow"
}


variable "datanow_version" {
    description     = "Version number of the DataNow container image."
    type            = string
    default         = "1.0.0"
}

variable "ingested_data_topic_name" {
   description  = "Name of the SNS topic for ngestion router."
   type = string
   default = "ingested_data_notification"
}

variable "processed_data_topic_name" {
   description  = "Name of the sns topic for processing router."
   type = string
   default = "processed_data_notification"
}

variable "outbound_security_groups" {
    description = "Security groups using the DataLake VPC which need VPC endpoints"
    type = list
    default = ["sg-055c7d63be1f52d6f", "sg-01b1b0411a5f4a798"]  # OneView, CPT-API Lambdas
}
