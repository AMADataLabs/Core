locals {
    environment               = regex("(?:.+/)(?P<environment>..*)", abspath(path.root)).environment
    account                   = lookup(var.accounts, local.environment)
    ecr_account               = local.environment == "sbx" ? local.account : "394406051370"

    subs                      = {
      environment       = local.environment
      account           = local.account
      ecr_account       = local.ecr_account
    }
    s3_lambda_bucket          = join("", [for word in split("%%", var.s3_lambda_bucket_template): lookup(local.subs, word, word)])
    s3_processed_data_bucket  = join("", [for word in split("%%", var.s3_processed_data_bucket_template): lookup(local.subs, word, word)])
    private_cname             = join("", [for word in split("%%", var.private_cname_template): lookup(local.subs, word, word)])
    public_cname              = join("", [for word in split("%%", var.public_cname_template): lookup(local.subs, word, word)])
    dynamodb_config_table     = join("", [for word in split("%%", var.dynamodb_config_table_template): lookup(local.subs, word, word)])

    lambda_names = {
        # API Endpoint Lambda
        endpoint                    = "${upper(var.project)}-${local.environment}-Endpoint"
        # API Authorizer Lambda
        authorizer                  = "${upper(var.project)}-${local.environment}-Authorizer"
        # ETL Lambda
        etl                         = "${upper(var.project)}-${local.environment}-ETL"
        # API Bulk Lambdas
        bulk_endpoint               = "${upper(var.project)}-${local.environment}-BulkEndpoint"
        bulk_authorizer             = "${upper(var.project)}-${local.environment}-BulkAuthorizer"
    }

    tags                = {
        Name                = "Data Labs ${var.project} Parameter"
        Environment         = local.environment
        Contact             = var.contact
        SystemTier          = "0"
        DRTier              = "0"
        DataClassification  = "N/A"
        BudgetCode          = var.budget_code
        Owner               = var.owner
        Group               = var.owner
        Department          = "HS"
        ProjectName         = var.project
        OS                  = "N/A"
        EOL                 = "N/A"
        MaintenanceWindow   = "N/A"
    }
}
