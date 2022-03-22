module "hello_world_java_dag_lambda" {
  source           = "app.terraform.io/AMA/lambda/aws"
  version          = "2.0.0"
  function_name    = local.dag_lambda
  lambda_name      = local.dag_lambda
  s3_lambda_bucket = local.s3_lambda_bucket
  s3_lambda_key    = "HelloWorldJava/DAG.zip"
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

  create_lambda_permission = true
  api_arn                  = "arn:aws:apigateway:us-east-1::/restapis/mb17ivas30/stages/sbx"

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS    = "datalabs.etl.dag.awslambda.DAGTaskWrapper"
      TASK_RESOLVER_CLASS   = "datalabs.etl.dag.resolve.TaskResolver"
      DYNAMODB_CONFIG_TABLE = local.dynamodb_config_table
    }
  }

  tag_name               = local.dag_lambda
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


module "hello_world_java_task_lambda" {
  source           = "app.terraform.io/AMA/lambda/aws"
  version          = "2.0.0"
  function_name    = local.task_lambda
  lambda_name      = local.task_lambda
  s3_lambda_bucket = local.s3_lambda_bucket
  s3_lambda_key    = "HelloWorldJava/Task.jar"
  handler          = "datalabs.task.LambdaFunction"
  runtime          = "java11"
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

  create_lambda_permission = true
  api_arn                  = "arn:aws:apigateway:us-east-1::/restapis/mb17ivas30/stages/sbx"

  environment_variables = {
    variables = {
      TASK_WRAPPER_CLASS    = "datalabs.etl.dag.lambda.DagTaskWrapper"
      TASK_RESOLVER_CLASS   = "datalabs.task.RuntimeTaskResolver"
      DYNAMODB_CONFIG_TABLE = local.dynamodb_config_table
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


module "lambda_sg" {
  source      = "app.terraform.io/AMA/security-group/aws"
  version     = "1.0.0"
  name        = "${local.project}-${local.environment}-hello-world-java-lambda-sg"
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


## Batch Task ###

module "batch_compute_environment" {
  source = "../../Module/BatchComputeEnvironment"

  name            = local.task_job
  project         = local.project
  environment     = local.environment
  security_groups = [module.batch_sg.security_group_id]
  subnets         = data.terraform_remote_state.infrastructure.outputs.subnet_ids

  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}

module "batch_job_queue" {
  source = "../../Module/BatchJobQueue"

  name                = local.task_job
  project             = local.project
  environment         = local.environment
  compute_environment = module.batch_compute_environment.arn

  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}

module "batch_job" {
  source = "../../Module/BatchJobDefinition"

  name                  = local.task_job
  project               = local.project
  environment           = local.environment
  service_role          = module.batch_compute_environment.service_role.arn
  ecr_account           = local.ecr_account
  image                 = "hello_world_java"
  image_version         = "1.0.0"
  resource_requirements = <<EOF
[
    {"type": "VCPU", "value": "1"},
    {"type": "MEMORY", "value": "2048"}
]
EOF
  environment_vars      = <<EOF
[
    {
        "name": "TASK_WRAPPER_CLASS",
        "value": "datalabs.etl.dag.ecs.DAGTaskWrapper"
    },
    {
        "name": "TASK_RESOLVER_CLASS",
        "value": "datalabs.etl.dag.resolve.TaskResolver"
    },
    {
        "name": "DYNAMODB_CONFIG_TABLE",
        "value": "${local.project}-configuration-${local.environment}"
    }
]
EOF

  tag_contact            = local.contact
  tag_budgetcode         = local.budget_code
  tag_owner              = local.owner
  tag_systemtier         = "0"
  tag_drtier             = "0"
  tag_dataclassification = "N/A"
  tag_notes              = "N/A"
  tag_eol                = "N/A"
  tag_maintwindow        = "N/A"
}

module "batch_sg" {
  source      = "app.terraform.io/AMA/security-group/aws"
  version     = "1.0.0"
  name        = "${local.project}-${local.environment}-hello-world-java-batch-sg"
  description = "Security group for Lambda VPC interfaces"
  vpc_id      = data.terraform_remote_state.infrastructure.outputs.vpc_id[0]

  ingress_with_cidr_blocks = [
    {
      from_port   = "443"
      to_port     = "443"
      protocol    = "tcp"
      description = "User-service ports"
      cidr_blocks = "10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
    {
      from_port   = "5432"
      to_port     = "5432"
      protocol    = "tcp"
      description = "PostgreSQL ports"
      cidr_blocks = "10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
    },
    {
      from_port   = "3306"
      to_port     = "3306"
      protocol    = "tcp"
      description = "MySQL ports"
      cidr_blocks = "10.96.64.0/20,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,199.164.8.1/32"
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
