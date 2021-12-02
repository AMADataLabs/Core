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


#####################################################################
# Lambda
#####################################################################

# Maven Java .jar program

module "lambda_java" {
  source  = "app.terraform.io/AMA/lambda/aws"
  version = "2.0.0"
  function_name       = local.lambda_names.java
  lambda_name         = local.lambda_names.java
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
  api_arn                     = "arn:aws:apigateway:us-east-1::/restapis/mb17ivas30/stages/sbx"

  environment_variables = {
    variables = {
        TASK_WRAPPER_CLASS      = "datalabs.etl.dag.awslambda.DAGTaskWrapper"
        TASK_RESOLVER_CLASS     = "datalabs.etl.dag.resolve.TaskResolver"
        DYNAMODB_CONFIG_TABLE   = local.dynamodb_config_table
    }
  }

  tag_name                          = local.lambda_names.java
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


