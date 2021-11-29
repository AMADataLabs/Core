#####################################################################
# Add application specific modules, data, locals, etc....           #
#####################################################################

# Generate a new random password with the "random" provider
resource "random_password" "database_password" {
  length = 16
  special = true
  override_special = "_%" #Supply your own list of special characters to use (if application can only handle certain special characters)
  # Reference with random_password.database_password.result
}


#####################################################################
# Secrets
#####################################################################

resource "aws_secretsmanager_secret" "database" {
  name        = "DataLabs/CPT/API/database-${local.environment}"
  description = "CPT API database credentials"

  recovery_window_in_days = var.days_to_recover

  #tags need to be added
}

# This need to be variablized
resource "aws_secretsmanager_secret_version" "database" {
  secret_id     = aws_secretsmanager_secret.database.id
  secret_string = jsonencode(
    {
        username = var.database_username
        password = random_password.database_password.result
        engine = "postgres"
        port = 5432
        dbname = "cpt"
        dbinstanceIdentifier = "cpt"
    }
  )
}


#####################################################################
# Security Groups
#####################################################################

module "lambda_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"
  name        = "cptapi-${local.environment}-lambda-sg"
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

}

module "rds_sg" {
  source  = "app.terraform.io/AMA/security-group/aws"
  version = "1.0.0"

  name        = "cptapi-${local.environment}-rds-sg"
  description = "Security group for RDS VPC interfaces"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "5432"
      to_port     = "5432"
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

}



#####################################################################
# Lambda
#####################################################################

#no vpc confg?
module "lambda_authorizer" {
  source  = "app.terraform.io/AMA/lambda/aws"
  version = "2.0.0"
  function_name       = local.lambda_names.authorizer
  lambda_name         = local.lambda_names.authorizer
  s3_lambda_bucket    = local.s3_lambda_bucket
  s3_lambda_key       = var.s3_lambda_key
  handler             = "awslambda.handler"
  runtime             = var.runtime
  create_alias        = false
  memory_size         = var.authorizer_lambda_memory_size
  timeout             = var.authorizer_lambda_timeout
  vpc_config = {
    subnet_ids              = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    security_group_ids      = [module.lambda_sg.security_group_id]
  }

  lambda_policy_vars = {
    account_id = local.account
    region     = var.region
    project    = var.project
  }

  create_lambda_permission    = true
  # api_arn                     = "arn:aws:execute-api:${local.region}:${local.account}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
  api_arn                   = module.api-gw.api_execution_arn

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS      = "datalabs.access.authorize.awslambda.AuthorizerLambdaTaskWrapper"
      TASK_CLASS              = "datalabs.access.authorize.task.AuthorizerTask"
      PASSPORT_URL            = var.passport_url
    }
  }

  tag_name                          = local.lambda_names.authorizer
  tag_environment                   = local.environment
  tag_contact                       = var.contact
  tag_budgetcode                    = var.budget_code
  tag_owner                         = var.owner
  tag_projectname                   = var.project
  tag_systemtier                    = "0"
  tag_drtier                        = "0"
  tag_dataclassification            = "N/A"
  tag_notes                         = "N/A"
  tag_eol                           = "N/A"
  tag_maintwindow                   = "N/A"
}


# Maven Java .jar program

module "lambda_etl_dag" {
  source  = "app.terraform.io/AMA/lambda/aws"
  version = "2.0.0"
  function_name       = local.lambda_names.etl
  lambda_name         = local.lambda_names.etl
  s3_lambda_bucket    = local.s3_lambda_bucket
  s3_lambda_key       = var.s3_lambda_key
  handler             = "awslambda.handler"
  runtime             = var.runtime
  create_alias        = false
  memory_size         = var.etl_lambda_memory_size
  timeout             = var.etl_lambda_timeout
  vpc_config = {
    subnet_ids              = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    security_group_ids      = [module.lambda_sg.security_group_id]
  }

  lambda_policy_vars = {
    account_id = local.account
    region     = var.region
    project    = var.project
  }

  create_lambda_permission    = true
  api_arn                   = module.api-gw.api_execution_arn

  environment_variables = {
    variables = {
        TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.DAGTaskWrapper"
        TASK_RESOLVER_CLASS     = "datalabs.etl.dag.resolve.TaskResolver"
        DYNAMODB_CONFIG_TABLE   = local.dynamodb_config_table
    }
  }

  tag_name                          = local.lambda_names.etl
  tag_environment                   = local.environment
  tag_contact                       = var.contact
  tag_budgetcode                    = var.budget_code
  tag_owner                         = var.owner
  tag_projectname                   = var.project
  tag_systemtier                    = "0"
  tag_drtier                        = "0"
  tag_dataclassification            = "N/A"
  tag_notes                         = "N/A"
  tag_eol                           = "N/A"
  tag_maintwindow                   = "N/A"
}


module "api-gw" {
  source            = "app.terraform.io/AMA/api-gateway/aws"
  version           = "2.1.0"
  api_template_vars = {
    region              = var.region
    account_id          = local.account
    project             = var.project
    environment         = local.environment
    authorizer_uri      = module.lambda_authorizer.function_invoke_arn
    descripton          = var.spec_description
  }
  stage_name        = local.environment
  environment       = local.environment
  api_name          = "granular"
  vpc_endpoint_id   = data.terraform_remote_state.infrastructure.outputs.vpc_endpoint_execapi_id
  resource_tag_name = lower(var.project)

  tag_name                         = "${var.project}-${local.environment}-apigw-api"
  tag_environment                   = local.environment
  tag_contact                       = var.contact
  tag_budgetcode                    = var.budget_code
  tag_owner                         = var.owner
  tag_projectname                   = var.project
  tag_systemtier                    = "0"
  tag_drtier                        = "0"
  tag_dataclassification            = "N/A"
  tag_notes                         = "N/A"
  tag_eol                           = "N/A"
  tag_maintwindow                   = "N/A"
}


data "aws_vpc_endpoint" "api_gw_vpc_endpoint" {
  tags = {
    Name = "${local.environment}-execute-api_vpc_endpoint"
  }

  vpc_id       = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
}

data "aws_network_interface" "apigw_endpoint_eni" {
  for_each = data.aws_vpc_endpoint.api_gw_vpc_endpoint.network_interface_ids
  id       = each.value
}

resource "aws_route53_zone" "private" {
  name = "cptapi.local"

  vpc {
    vpc_id = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]
  }

  tags = {

    Name        =  upper("${var.project}-${local.environment}-apigw-r53-zone")
    Environment =  upper(local.environment)
    Contact     =  upper(var.contact)
    SystemTier  =  "0"
    DRTier      =  "0"
    DataClassification = upper("N/A")
    BudgetCode  =   upper(var.budget_code)
    Owner       =  upper(var.owner)
    ProjectName =  upper(var.project)
    Notes       =  upper("N/A")
    EOL         =  upper("N/A")
    MaintenanceWindow =  upper("N/A")
  }

}