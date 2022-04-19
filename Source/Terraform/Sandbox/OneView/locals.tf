locals {
  accounts = {
    sbx = "644454719059"
    dev = "191296302136"
    tst = "194221139997"
    stg = "340826698851"
    prd = "285887636563"
  }

  region = local.region

  host_suffixes = {
    sbx = "-sbx"
    dev = "-dev"
    tst = "-test"
    stg = "-intg"
    prd = ""
  }

  system_tier = "Application"
  na          = "N/A"
  budget_code = "PBW"
  owner       = "DataLabs"
  project     = "OneView"

  environment = data.aws_ssm_parameter.account_environment.value
  account     = lookup(local.accounts, local.environment)
  ecr_account = local.environment == "sbx" ? local.account : "394406051370"

  dag_lambda            = "${local.project}-${local.environment}-OneViewDag"
  task_lambda           = "${local.project}-${local.environment}-OneViewDag"
  task_job              = "OneViewDag"
  s3_lambda_bucket      = "ama-${local.environment}-datalake-lambda-us-east-1"
  dynamodb_config_table = "DataLake-configuration-${local.environment}"

  tags = {
    Name               = "Data Labs OneView Parameter"
    Env                = local.environment
    Contact            = data.aws_ssm_parameter.contact.value
    SystemTier         = local.system_tier
    DRTier             = local.na
    DataClassification = local.na
    BudgetCode         = local.budget_code
    Owner              = local.owner
    Group              = local.owner
    Department         = "HSG"
    ProjectName        = local.project
    OS                 = local.na
    EOL                = local.na
    MaintenanceWindow  = local.na
  }
  function_names = {
    etl = "${var.project}-ETL-${var.environment}"
  }
  runtime = "python3.7"
}
