data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "terraform_state_bucket" {
    name = "/DataLabs/Terraform/state_bucket"
}


data "aws_ssm_parameter" "terraform_locks_database" {
    name = "/DataLabs/Terraform/locks_database"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}


locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "Data Labs"
    notes               = ""
    tags = {
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
