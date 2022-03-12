locals {
  ### Static Constants ###

  environments = {
    sandbox = "sbx"
    dev     = "dev"
    test    = "tst"
    prod    = "prd"
  }

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

  public_domain = "ama-assn.org"
  smtp_domain   = "amamx.ama-assn.org"

  project     = "DataLake"
  owner       = "DataLabs"
  contact     = "DataLabs@ama-assn.org"
  department  = "HS"
  group       = "DataLabs"
  budget_code = "PBW"

  python_runtime = "python3.7"


  ### Dynamic Constants ###

  environment = regex("(?:.+/)(?P<environment>..*)", abspath(path.root)).environment
  account     = lookup(local.accounts, local.environment)
  ecr_account = local.environment == "sbx" ? local.account : "394406051370"

  datanow_image    = "${var.datanow_image_prefix}-${local.environment}"
  s3_lambda_bucket = "ama-${local.environment}-datalake-${var.s3_lambda_bucket_base_name}-us-east-1"

  host_suffix    = lookup(var.host_suffixes, local.environment)
  datanow_domain = "${var.datanow_host_prefix}${local.host_suffix}.${var.domain}"

  parameter_name_prefix = "/${local.project}/${local.environment}/"

  lambda_names = {
    scheduler      = "${local.project}-${local.environment}-Scheduler"
    dag_processor  = "${local.project}-${local.environment}-DAGProcessor"
    task_processor = "${local.project}-${local.environment}-TaskProcessor"
  }

  topic_names = {
    ingested_data  = "${local.project}-${local.environment}-ingested-data"
    processed_data = "${local.project}-${local.environment}-processed-data"
    scheduler      = "${local.project}-${local.environment}-Scheduler"
    dag_processor  = "${local.project}-${local.environment}-DAGProcessor"
    task_processor = "${local.project}-${local.environment}-TaskProcessor"
  }

  tags = {
    Name               = "Data Labs ${local.project} Parameter"
    Environment        = local.environment
    Contact            = local.contact
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    BudgetCode         = local.budget_code
    Owner              = local.owner
    Group              = local.group
    Department         = local.department
    ProjectName        = local.project
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
  }
}
