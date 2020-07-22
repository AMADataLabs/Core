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
