variable "project" {
    description     = "Project name used in tags and names to distinguish resources."
    type            = string
}


variable "datanow_image" {
    description     = "ECR repository (image name) for the DataNow container image."
    type            = string
    default         = "datanow"
}


variable "datanow_version" {
    description     = "Version number of the DataNow container image."
    type            = string
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "ingested_data_bucket" {
    name = "/DataLabs/${var.project}/ingested_data_bucket"
}


data "aws_ssm_parameter" "processed_data_bucket" {
    name = "/DataLabs/${var.project}/processed_data_bucket"
}


data "aws_iam_policy" "ecs_task_execution" {
    arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


data "aws_caller_identity" "account" {}


data "aws_region" "current" {}


data "aws_route53_zone" "amaaws" {
    name = "amaaws.org"
}


data "aws_acm_certificate" "amaaws" {
    domain = "*.amaaws.org"
}


locals {
    aws_environment     = data.aws_ssm_parameter.account_environment.value
    contact             = data.aws_ssm_parameter.contact.value
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    tags = {
        Env                 = local.aws_environment
        Contact             = local.contact
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        Project             = var.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
