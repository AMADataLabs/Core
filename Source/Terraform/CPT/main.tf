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

    tags = {
        Name = "Data Labs Datalake Terraform State Bucket"
        Env                 = var.environment
        Contact             = var.contact
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Notes               = local.notes
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}


# resource "aws_iam_role" "cpt_lambda_role" {
#     name = "DataLabsCPTLambdaExecution"

#     assume_role_policy = <<EOF
# {
#     "Version": "sts:AssumeRole",
#     "Principal": {
#         "Service": "lambda.amazonaws.com"
#     },
#     "Effect": "Allow",
# }
# EOF
# }


# resource "aws_lambda_function" "convert_cpt_etl" {
#     filename        = "../../../Build/CPT/app.zip"
#     function_name   = "ConvertCPT"

# }


variable "username" {}

variable "password" {}


variable "environment" {
    description = "AWS Account Environment"
    type        = string
    default     = "Sandbox"
}


variable "contact" {
    description = "Email address of the Data Labs contact."
    type        = string
    default     = "DataLabs@ama-assn.org"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = "Experimental"
}