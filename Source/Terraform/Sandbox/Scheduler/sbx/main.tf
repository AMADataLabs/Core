#####################################################################
# Security Group
#####################################################################

module "scheduler_sg" {
  source      = "app.terraform.io/AMA/security-group/aws"
  version     = "1.0.0"
  name        = "${var.project}-${local.environment}-scheduler-sg"
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


#####################################################################
# AWS Batch
#####################################################################

##### Compute Environment #####

resource "aws_batch_compute_environment" "ecs_scheduler_env" {
  compute_environment_name = "ecs-scheduler-env"

  compute_resources {
    max_vcpus = 2

    security_group_ids = [
      module.scheduler_sg.security_group_id
    ]

    #NOTE: HADI, are you sure? ask Peter
    subnets = data.terraform_remote_state.infrastructure.outputs.subnet_ids
    # subnets = ["subnet-0a508711165923924"]
    # subnets = ["arn:aws:ec2:us-east-1:644454719059:subnet/subnet-0a508711165923924"]

    type = "FARGATE"
  }

  service_role = aws_iam_role.scheduler_batch_service_role.arn
  # service_role = "arn:aws:iam::${local.account}:role/datalake-${local.environment}-task-exe-role"
  type       = "MANAGED"
  depends_on = [aws_iam_role_policy_attachment.aws_batch_service_role]

  tags = {
    Name               = "${var.project}-${local.environment}-ecs-scheduler-env"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}


##### Job Queue #####

resource "aws_batch_job_queue" "ecs_scheduler_job_queue" {
  name     = "ecs-scheduler-job-queue"
  state    = "ENABLED"
  priority = 1
  compute_environments = [
    aws_batch_compute_environment.ecs_scheduler_env.arn,
  ]

  tags = {
    Name               = "${var.project}-${local.environment}-ecs-scheduler-job-queue"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

##### Scheduler Job Definition #####
resource "aws_batch_job_definition" "ecs-scheduler-job-definition" {
  name = "ecs-scheduler-job-definition"
  type = "container"
  platform_capabilities = [
    "FARGATE",
  ]

  container_properties = <<CONTAINER_PROPERTIES
{
  "command": ["python","task.py","{\"dag\": \"ECS_SCHEDULER\", \"type\": \"DAG\", \"execution_time\": \"2020-11-10 21:30:00.000\"}"],
  "image": "644454719059.dkr.ecr.us-east-1.amazonaws.com/datalake-sbx",
  "fargatePlatformConfiguration": {
    "platformVersion": "1.3.0"
  },
  "resourceRequirements": [
    {"type": "VCPU", "value": "1"},
    {"type": "MEMORY", "value": "2048"}
  ],
  "executionRoleArn": "arn:aws:iam::${local.account}:role/${lower(var.project)}-${local.environment}-task-exe-role",
  "jobRoleArn": "${aws_iam_role.scheduler_batch_service_role.arn}",
  "environment": [
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
        "value": "DataLake-configuration-${local.environment}"
      }
  ]
}
CONTAINER_PROPERTIES
}


##### Scheduler Service Role #####

resource "aws_iam_role" "scheduler_batch_service_role" {
  name               = "scheduler_batch_service_role"
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
    {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
        "Service": [
            "batch.amazonaws.com",
            "ecs-tasks.amazonaws.com"
        ]
        }
    }
    ]
}
EOF

  tags = {
    Name               = "${var.project}-${local.environment}-scheduler-batch-service-role"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

resource "aws_iam_role_policy_attachment" "aws_batch_service_role" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role_policy_attachment" "secret_manager_read_write" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

#### ECS Task Role ####

data "aws_iam_policy_document" "ecs_task_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "${lower(var.project)}-${local.environment}-task-exe-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_role.json
  description        = "Allows ECS tasks to call AWS services on your behalf."

  tags = {
    Name               = "ECS Task Role for OneView"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

data "aws_iam_policy" "AmazonECSTaskExecutionRolePolicy" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = data.aws_iam_policy.AmazonECSTaskExecutionRolePolicy.arn
}


data "aws_iam_policy" "AmazonSSMReadOnlyAccess" {
  arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

resource "aws_iam_role_policy_attachment" "ecs_task_ssm" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = data.aws_iam_policy.AmazonSSMReadOnlyAccess.arn
}

#### DynamoDB GetItem Policy ####

data "aws_iam_policy_document" "ecs_task_dynamodb_get_item" {
  statement {
    actions = [
      "dynamodb:GetItem",
      # "dynamodb:PutItem"
    ]

    resources = [
      "arn:aws:dynamodb:us-east-1:${local.account}:table/DataLake-configuration-${local.environment}",
      "arn:aws:dynamodb:us-east-1:${local.account}:table/DataLake-dag-state-${local.environment}"
    ]
  }
}

resource "aws_iam_policy" "ecs_task_dynamodb_get_item_policy" {
  name        = "${lower(var.project)}-${local.environment}-task-dynamodb-get-item-policy"
  policy      = data.aws_iam_policy_document.ecs_task_dynamodb_get_item.json
  description = "Allows AWS Batch jobs to get table items from DynamoDB DataLake-configuration-${local.environment} table"

  tags = {
    Name               = "ECS Task Policy for AWS Batch"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_dynamodb_get_item_role" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = aws_iam_policy.ecs_task_dynamodb_get_item_policy.arn
}

#### DynamoDB PutItem and DeleteItem Policy ####

data "aws_iam_policy_document" "ecs_task_dynamodb_put_item" {
  statement {
    actions = [
      "dynamodb:PutItem",
      "dynamodb:DeleteItem"
    ]

    resources = [
      "arn:aws:dynamodb:us-east-1:644454719059:table/DataLake-scheduler-locks-${local.environment}"
    ]
  }
}

resource "aws_iam_policy" "ecs_task_dynamodb_put_item_policy" {
  name        = "${lower(var.project)}-${local.environment}-task-dynamodb-put-item-policy"
  policy      = data.aws_iam_policy_document.ecs_task_dynamodb_put_item.json
  description = "Allows AWS Batch jobs to put and delete table items into/fromye DynamoDB DataLake-scheduler-locks-${local.environment} table"

  tags = {
    Name               = "ECS Task Policy for AWS Batch"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_dynamodb_put_item_role" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = aws_iam_policy.ecs_task_dynamodb_put_item_policy.arn
}

#### SNS Publish Policy ####

data "aws_iam_policy_document" "ecs_task_sns_publish" {
  statement {
    actions = [
      "SNS:Publish"
    ]

    resources = [
      "arn:aws:sns:us-east-1:644454719059:DataLake-sbx-DAGProcessor"
    ]
  }
}

resource "aws_iam_policy" "ecs_task_sns_publish_policy" {
  name        = "${lower(var.project)}-${local.environment}-task-sns-publish-policy"
  policy      = data.aws_iam_policy_document.ecs_task_sns_publish.json
  description = "Allows AWS Batch jobs to put and delete table items into/fromye DynamoDB DataLake-scheduler-locks-${local.environment} table"

  tags = {
    Name               = "ECS Task Policy for publishing sns topics"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_sns_publish_role" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = aws_iam_policy.ecs_task_sns_publish_policy.arn
}

#### DynamoDB PutItem Policy ####

data "aws_iam_policy_document" "ecs_task_dynamodb_put_item_dag_state" {
  statement {
    actions = [
      "dynamodb:PutItem",
    ]

    resources = [
      "arn:aws:dynamodb:us-east-1:644454719059:table/DataLake-dag-state-${local.environment}"
    ]
  }
}

resource "aws_iam_policy" "ecs_task_dynamodb_put_item_policy_dag_state" {
  name        = "${lower(var.project)}-${local.environment}-task-dynamodb-put-item-policy_dag_state"
  policy      = data.aws_iam_policy_document.ecs_task_dynamodb_put_item_dag_state.json
  description = "Allows AWS Batch jobs to put table items into DynamoDB DataLake-dag-state-${local.environment} table"

  tags = {
    Name               = "ECS Task Policy for AWS Batch"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_dynamodb_put_item_role_dag_state" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = aws_iam_policy.ecs_task_dynamodb_put_item_policy_dag_state.arn
}

#### S3 Get and List policy ####

data "aws_iam_policy_document" "ecs_task_s3_get_list_object" {
  statement {
    actions = [
      "s3:Get*",
      "s3:List*",
    ]

    resources = [
      "arn:aws:s3:::ama-${local.environment}-datalake-scheduler-us-east-1",
      "arn:aws:s3:::ama-${local.environment}-datalake-scheduler-us-east-1/*"
    ]
  }
}

resource "aws_iam_policy" "ecs_task_s3_get_list_object_policy" {
  name        = "${lower(var.project)}-${local.environment}-task-s3-get-list-object"
  policy      = data.aws_iam_policy_document.ecs_task_s3_get_list_object.json
  description = "Allows AWS Batch jobs to get objects from ama-${local.environment}-datalake-scheduler-us-east-1 Bucket"

  tags = {
    Name               = "ECS Task Policy for AWS Batch"
    Environment        = local.environment
    Contact            = var.contact
    BudgetCode         = var.budget_code
    Owner              = var.owner
    ProjectName        = var.project
    SystemTier         = "0"
    DRTier             = "0"
    DataClassification = "N/A"
    Notes              = "N/A"
    OS                 = "N/A"
    EOL                = "N/A"
    MaintenanceWindow  = "N/A"
    Group              = "Health Solutions"
    Department         = "DataLabs"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3_get_list_object_role" {
  role       = aws_iam_role.scheduler_batch_service_role.name
  policy_arn = aws_iam_policy.ecs_task_s3_get_list_object_policy.arn
}
