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

variable "days_to_recover" {
   description  = "AWS Secrets Manager Recovery Window in Days"
   type = number
   default = 0
}


#Task Definition Variables

variable "datanow_image_prefix" {
   description  = "The image name prefix of the container image stored in ECR"
   type = string
   default = "datanow"
}

variable "datanow_version" {
   description  = "The version of the image stored in the ECR repository"
   type = string
   default = "1.1.0"
}

variable "datanow_host_prefix" {
    description = "Host name prefix for DataNow"
    type        = string
    default     = "datanow"
}

variable "s3_lambda_bucket_base_name" {
   description  = "Base name of the S3 bucket where Lambda function code artifacts are stored."
   type = string
   default = "lambda"
}

variable "s3_scheduler_lambda_key" {
   description  = "CPT API Lambda function code artifact name."
   type = string
   default = "Scheduler.zip"
}

variable "runtime" {
   description  = "Lambda function runtime."
   type = string
   default = "python3.7"
}

variable "lambda_memory_size" {
   description  = "Router Lambda function memory size in MB."
   type = number
   default = 1024
}

variable "lambda_timeout" {
   description  = "Router Lambda function timeout in seconds."
   type = number
   default = 10
}

variable "s3_data_base_path" {
   description  = "Base path in the Data Lake S3 bucket where CPT API data is located."
   type = string
   default = "AMA/CPT"
}

variable "public_certificate_arn" {
    description = "ARN of certificate for AMA-wide CNAME"
    type        = string
    default     = "arn:aws:acm:us-east-1:191296302136:certificate/41af8728-d9c8-46e8-8ec0-2420cf8a5924"
}

variable "host_suffixes" {
   description  = "Host name suffixes by environment."
   default = {
     sbx = "-sbx"
     dev = "-dev"
     tst = "-test"
     stg = "-stg"
     itg = "-intg"
     prd = ""
   }
}

variable "domain" {
    description = "Base domain name for public CNAMEs"
    type        = string
    default     = "amaaws.org"
}
