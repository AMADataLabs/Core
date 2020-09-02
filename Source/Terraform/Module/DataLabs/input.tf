variable "project" {
    description     = "Project name used in tags and names to distinguish resources."
    type            = string
}


variable "bitbucket_username" {
    description     = "BitBucket username used for pulling code."
    type            = string
    default         = "hsgdatalabs"
}


variable "bitbucket_app_password" {
    description     = "BitBucket App password used for pulling code."
    type            = string
}


data "aws_caller_identity" "account" {}


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
    owner               = "DataLabs"
    region              = "us-east-1"
    tags = {
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
