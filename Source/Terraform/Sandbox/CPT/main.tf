provider "aws" {
    region = "us-east-1"
}


module "cpt" {
    source = "../../Module/CPT"

    rds_instance_name   = "database-test-ui"
    rds_instance_class  = "db.t2.micro"
    rds_storage_type    = "gp2"
    database_name       = "sample"
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


variable "password" {}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    tags                = {
        Name = "Data Labs CPT Parameter"
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
