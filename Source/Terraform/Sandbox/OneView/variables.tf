variable "project" {
    description     = "Project name used in tags and names to distinguish resources."
    type            = string
    default         = "OneView"
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

variable "contact" {
   description  = "Email of the contact for this app stack."
   type = string
   default = "DataLabs@ama-assn.org"
}


variable "owner" {
   description  = "Name of the owner of this application."
   type = string
   default = "Data Labs"
}


variable "budget_code" {
   description  = "Budget code for accounting purposes."
   type = string
   default = "PBW"
}

variable "account" {
   description  = "AWS account into which this app stack is deployed."
   type = string
    default = "644454719059"
}


variable "rds_instance_class" {
    description = "RDS instance class"
    type        = string
    default     = "db.m5.large"
}


variable "db_instance_allocated_storage" {
   description  = "RDS instance allocated storage size in GB."
   type = number
   default = 20
}


variable "max_allocated_storage" {
   description  = "RDS instance allocated storage maximum size in GB."
   type = number
   default = 1000
}


variable "db_engine_version" {
   description  = "RDS instance engine version."
   type = string
   default = "11.10"
}


variable "enable_multi_az" {
   description  = "Whether to enable multi-availability-zone deployment for the RDS instance."
   type = bool
   default = false
}


variable "ssl_policy" {
   description = "SSL Policy Variable"
   type = string
   default = "ELBSecurityPolicy-2020-10"
}


variable "rds_storage_type" {
    description = "RDS storage type"
    type        = string
    default     = "gp2"
}


variable "database_username" {
  type = string
  description = "The master username for the RDS instance"
  default = "datalabs"
}


variable "lambda_code_bucket" {
    description     = "Name of the S3 bucket used to hold Lambda function code artifacts."
    type            = string
    default         = "ama-hsg-datalabs-lambda-code-sandbox"
}


variable "etl_memory_size" {
    description = "memory size in Mb"
    type        = number
    default     = 3072
}


variable "etl_timeout" {
    description = "timeout in seconds"
    type        = number
    default     = 15
}


variable "etcd_host" {
    description = "timeout in seconds"
    type        = string
    default     = 15
}
