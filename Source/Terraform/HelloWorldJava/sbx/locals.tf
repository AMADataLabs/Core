locals {
  ### Static Constants ###

  accounts = {
    sbx = "644454719059"
    dev = "191296302136"
    tst = "194221139997"
    stg = "340826698851"
    prd = "285887636563"
  }

  region = "us-east-1"

  host_suffixes = {
    sbx = "-sbx"
    dev = "-dev"
    tst = "-test"
    stg = "-intg"
    prd = ""
  }

  project     = "DataLake"
  owner       = "DataLabs"
  contact     = "DataLabs@ama-assn.org"
  budget_code = "PBW"


  ### Dynamic Constants ###

  environment = regex("(?:.+/)(?P<environment>..*)", abspath(path.root)).environment
  account     = lookup(local.accounts, local.environment)
  ecr_account = local.environment == "sbx" ? local.account : "394406051370"

  dag_lambda            = "${local.project}-${local.environment}-HelloWorldJavaDAG"
  task_lambda           = "${local.project}-${local.environment}-HelloWorldJavaTask"
  task_job              = "${local.project}-${local.environment}-HelloWorldJavaTask"
  s3_lambda_bucket      = "ama-${local.environment}-datalake-lambda-us-east-1"
  dynamodb_config_table = "DataLake-configuration-${local.environment}"

  tags = {
    Name               = "Data Labs ${local.project} Parameter"
    Environment        = local.environment
    Contact            = local.contact
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    BudgetCode         = local.budget_code
    Owner              = local.owner
    Group              = local.owner
    Department         = "HS"
    ProjectName        = local.project
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
  }
}
