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
