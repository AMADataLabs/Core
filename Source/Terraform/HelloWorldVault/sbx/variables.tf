variable "database_host" {
  description = "Database host."
  type        = string
  default     = "cpt-api-sbx-db.c3mn4zysffxi.us-east-1.rds.amazonaws.com"
}

variable "database_port" {
  description = "Database port."
  type        = string
  default     = "5432"
}

variable "database_backend" {
  description = "Database SQLAlchemy backend."
  type        = string
  default     = "postgresql+psycopg2"
}

variable "database_name" {
  description = "Database name."
  type        = string
  default     = "vault"
}

variable "database_username" {
  description = "Database username."
  type        = string
  default     = "helloworld"
}

variable "database_password" {
  description = "Database password."
  type        = string
  default     = "OpenSesame123"
}
