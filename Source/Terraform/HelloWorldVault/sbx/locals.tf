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

  task_lambda           = "${local.project}-${local.environment}-HelloWorldVault"
  s3_lambda_bucket      = "ama-${local.environment}-datalake-lambda-us-east-1"
}
