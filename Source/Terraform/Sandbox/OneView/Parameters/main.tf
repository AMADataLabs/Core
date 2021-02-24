provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


resource "aws_kms_key" "oneview" {
  description   = "${local.project} KMS key"
  tags          = merge(local.tags, {Name = "${local.project} parameter encryption key"})
}


resource "aws_kms_alias" "oneview" {
  name          = "alias/DataLabs/${local.project}"
  target_key_id = aws_kms_key.oneview.key_id
}

resource "aws_secretsmanager_secret" "database" {
    name        = "DataLabs/OneView/database"
    description = "Oneview database credentials"
    kms_key_id  = aws_kms_key.oneview.arn

    tags = merge(local.tags, {Name = "Data Labs ${local.project} Database Secret"})
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id     = aws_secretsmanager_secret.database.id
  secret_string = jsonencode(
    {
        username = "datalabs"
        password = var.database_password
        engine = "postgres"
        port = 5432
        dbname = "oneview"
        dbinstanceIdentifier = "oneview"
    }
  )
}

locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    project             = "OneView"
    tags                = {
        Name                = "Data Labs ${local.project} Parameter"
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
