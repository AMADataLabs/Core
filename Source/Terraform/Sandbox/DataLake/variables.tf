variable "project" {
   description  = "Name of the project used primarily in resource names."
   type = string
   default = "DataLake"
}

variable "contact" {
   description  = "Email of the contact for this app stack."
   type = string
   default = "DataLabs@ama-assn.org"
}

variable "owner" {
   description  = "Name of the owner of this application."
   type = string
   default = "DataLabs"
}

variable "budget_code" {
   description  = "Budget code for accounting purposes."
   type = string
   default = "PBW"
}

variable "accounts" {
   description  = "AWS accounts into which this app stack is deployed."
   default = {
     sbx = "644454719059"
     dev = "191296302136"
     tst = "194221139997"
     stg = "340826698851"
     itg = "285887636563"
     prd = "285887636563"
   }
}

variable "region" {
   description  = "AWS region into which this app stack is deployed."
   type = string
   default = "us-east-1"
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
    default     = 60
}

variable "datanow_image" {
    description     = "ECR repository (image name) for the DataNow container image."
    type            = string
    default         = "datanow"
}

variable "datanow_version" {
    description     = "Version number of the DataNow container image."
    type            = string
    default         = "1.1.0"
}

variable "datanow_host_prefix" {
    description = "Host name prefix for DataNow"
    type        = string
    default     = "datanow"
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

variable "host_suffixes" {
   description  = "Host name suffixes by environment."
   default = {
     sbx = "-sbx"
     dev = "-dev"
     tst = "-test"
     stg = "-intg"
     prd = ""
   }
}

variable "domain" {
    description = "Base domain name for public CNAMEs"
    type        = string
    default     = "amaaws.org"
}
