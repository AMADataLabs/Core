variable "rds_instance_name" {
    description = "RDS instance identifier"
    type        = string
    default     = "datalabs-api-backend"
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


variable "database_name" {
    description = "database name"
    type        = string
    default     = "cpt-api"
}
