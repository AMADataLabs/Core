resource "aws_db_instance" "oneview_database" {
    identifier                    = local.rds_instance_name
    instance_class                = var.rds_instance_class
    storage_type                  = var.rds_storage_type
    port                          = local.rds_port
    name                          = local.database_name
    allocated_storage             = 20
    engine                        = local.rds_engine
    engine_version                = "11.8"
    parameter_group_name          = "default.postgres11"
    max_allocated_storage         = 1000
    publicly_accessible           = true
    copy_tags_to_snapshot         = true
    performance_insights_enabled  = true
    skip_final_snapshot           = true
    username                      = local.database_username
    password                      = local.database_password

    tags = merge(local.tags, {Name = "${var.project} Database"})
}

locals {
    region              = "us-east-1"
    spec_title          = "${var.project} OneView"
    spec_description    = "${var.project} OneView Phase I"
    na                  = "N/A"
    owner               = "DataLabs"
    database_secret     = jsondecode(data.aws_secretsmanager_secret_version.database.secret_string)
    rds_instance_name   = local.database_secret["dbinstanceIdentifier"]
    rds_engine          = local.database_secret["engine"]
    rds_port          = local.database_secret["port"]
    database_name       = local.database_secret["dbname"]
    database_username   = local.database_secret["username"]
    database_password   = local.database_secret["password"]
    tags = {
        Env = data.aws_ssm_parameter.account_environment.value
        Contact = data.aws_ssm_parameter.contact.value
        SystemTier = "Application"
        DRTier = local.na
        DataClassification = local.na
        BudgetCode = "PBW"
        Owner = local.owner
        Group = local.owner
        Project = var.project
        Department = "HSG"
        OS = local.na
        EOL = local.na
        MaintenanceWindow = local.na
    }
}