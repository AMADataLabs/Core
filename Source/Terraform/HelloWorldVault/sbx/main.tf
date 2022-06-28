### Main Component Resources ###

module "hello_world_vault_lambda" {
  source           = "app.terraform.io/AMA/lambda/aws"
  version          = "2.4.0"
  function_name    = local.task_lambda
  lambda_name      = local.task_lambda
  s3_lambda_bucket = local.s3_lambda_bucket
  s3_lambda_key    = "HelloWorldVault.zip"
  handler          = "awslambda.handler"
  runtime          = "python3.7"
  create_alias     = false
  memory_size      = 3072
  timeout          = 10
  vpc_config = {
    subnet_ids         = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    security_group_ids = [module.lambda_sg.security_group_id]
  }

  lambda_policy_vars = {
    account_id = local.account
    region     = local.region
    project    = local.project
  }

  create_lambda_permission = false

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS = "datalabs.awslambda.TaskWrapper"
      TASK_CLASS         = "datalabs.example.vault.task.CRUDTask"
      DATABASE_HOST      = var.database_host
      DATABASE_PORT      = var.database_port
      DATABASE_BACKEND   = var.database_backend
      DATABASE_NAME      = var.database_name
      DATABASE_USERNAME  = var.database_username
      DATABASE_PASSWORD  = var.database_password
    }
  }

  tag_name               = local.task_lambda
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}


### Security Groups ###

module "lambda_sg" {
  source      = "app.terraform.io/AMA/security-group/aws"
  version     = "3.0.0"
  name        = "${local.project}-${local.environment}-hello-world-vault-lambda-sg"
  description = "Security group for Lambda VPC interfaces"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "User-service ports"
      cidr_blocks = "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = "-1"
      to_port     = "-1"
      protocol    = "-1"
      description = "outbound ports"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  tag_name               = "${local.project}-${local.environment}-hello-world-vault-lambda-sg"
  tag_environment        = local.environment
  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_projectname        = local.project
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}
