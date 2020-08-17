provider "aws" {
    region = "us-east-1"
}


module "cpt" {
    source = "../../Module/CPT"

    rds_instance_name   = "database-test-ui"
    rds_instance_class  = "db.t2.micro"
    rds_storage_type    = "gp2"
    database_name       = "sample"
    project             = local.project
    passport_url        = "https://amapassport-test.ama-assn.org/auth/entitlements/list/CPTAPI"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    project             = "CPT"
    tags                = {
        Name                = "Data Labs CPT Parameter"
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        Project             = local.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
