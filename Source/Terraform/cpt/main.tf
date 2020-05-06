provider "aws" {
    region = "us-east-1"
}

resource "aws_db_instance" "cpt_api_database" {
  identifier                    = "database-test-ui"  # FIXME: change to "datalabs-api-backend"
  name                          = "sample"
  instance_class                = "db.t2.micro"
  allocated_storage             = 20
  storage_type                  = "gp2"
  engine                        = "postgres"
  engine_version                = "11.5"
  parameter_group_name          = "default.postgres11"
  max_allocated_storage         = 1000
  publicly_accessible           = true
  copy_tags_to_snapshot         = true
  performance_insights_enabled  = true
  skip_final_snapshot           = true
  username                      = var.username
  password                      = var.password
}


variable "username" {}

variable "password" {}