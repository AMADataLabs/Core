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
  name = "DataLabs/${var.project}/database"
}

data "aws_secretsmanager_secret_version" "database" {
  secret_id = data.aws_secretsmanager_secret.database.id
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}
