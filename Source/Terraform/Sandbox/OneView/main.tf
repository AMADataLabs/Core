provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


module "oneview" {
    source = "../../Module/OneView"

    rds_instance_class      = "db.m5.large"
    rds_storage_type        = "gp2"
    project                 = local.project
    endpoint_memory_size    = 3072
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    project             = "OneView"
    tags                = {
        Name                = "Data Labs OneView Parameter"
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        ProjectName             = local.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
