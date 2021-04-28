provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


data "aws_caller_identity" "account" {}


#####################################################################
# Datalake - S3 Buckets and Event Notifications                     #
#####################################################################

##### BEGIN REMOVE #####
resource "aws_s3_bucket" "datalabs_lambda_code_bucket" {
    bucket = var.lambda_code_bucket

    lifecycle {
        prevent_destroy = true
    }

    tags = merge(local.tags, {Name = "Data Labs Lambda Code Bucket"})
}


resource "aws_s3_bucket_public_access_block" "datalabs_lambda_code_bucket_public_access_block" {
    bucket = var.lambda_code_bucket

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true

    depends_on = [aws_s3_bucket.datalabs_lambda_code_bucket]
}
##### END REMOVE #####

module "s3_ingested_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-datalake-ingested-data-${var.region}"

  lifecycle_rule = [
    {
      enabled = true

      transition = [
        {
          days          = 90
          storage_class = "STANDARD_IA"
          },
          {
          days          = 365
          storage_class = "GLACIER"
        }
      ]

    }
  ]

  app_name                          = lower(var.project)
  app_environment                   = var.environment

  tag_name                          = "${var.project}-${var.environment}-s3-ingested-data"
  tag_environment                   = var.environment
  tag_contact                       = local.contact
  tag_budgetcode                    = local.budget_code
  tag_owner                         = local.owner
  tag_projectname                   = local.project
  tag_systemtier                    = local.tier
  tag_drtier                        = local.tier
  tag_dataclassification            = local.na
  tag_notes                         = local.na
  tag_eol                           = local.na
  tag_maintwindow                   = local.na
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


resource "aws_s3_bucket_notification" "sns_ingested_data" {
    bucket = module.s3_ingested_data.bucket_id
    topic {
        topic_arn           = module.sns_ingested_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


module "s3_processed_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-datalake-processed-data-${var.region}"

  lifecycle_rule = [
    {
      enabled = true

      transition = [
        {
          days          = 90
          storage_class = "STANDARD_IA"
          },
          {
          days          = 365
          storage_class = "GLACIER"
        }
      ]


    }
  ]

  app_name                          = lower(var.project)
  app_environment                   = var.environment

  tag_name                          = "${var.project}-${var.environment}-s3-processed-data"
  tag_environment                   = var.environment
  tag_contact                       = local.contact
  tag_budgetcode                    = local.budget_code
  tag_owner                         = local.owner
  tag_projectname                   = local.project
  tag_systemtier                    = local.tier
  tag_drtier                        = local.tier
  tag_dataclassification            = local.na
  tag_notes                         = local.na
  tag_eol                           = local.na
  tag_maintwindow                   = local.na
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


resource "aws_s3_bucket_notification" "sns_processed_data" {
    bucket = module.s3_processed_data.bucket_id
    topic {
        topic_arn           = module.sns_processed_data.topic_arn
        events              = ["s3:ObjectCreated:*"]
    }
}


module "lambda_code_bucket" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-s3.git?ref=2.0.0"

  enable_versioning = true
  bucket_name = "ama-${var.environment}-${lower(var.project)}-lambda-code-${var.region}"

  app_name                          = lower(var.project)
  app_environment                   = var.environment

  tag_name                          = "${var.project}-${var.environment}-s3-lambda-code"
  tag_environment                   = var.environment
  tag_contact                       = local.contact
  tag_budgetcode                    = local.budget_code
  tag_owner                         = local.owner
  tag_projectname                   = local.project
  tag_systemtier                    = local.tier
  tag_drtier                        = local.tier
  tag_dataclassification            = local.na
  tag_notes                         = local.na
  tag_eol                           = local.na
  tag_maintwindow                   = local.na
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


#####################################################################
# Datalake - SNS Topics and Subscriptions                           #
#####################################################################

module "sns_ingested_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = "ingested_data_notification-${var.environment}"
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_ingested_data.bucket_id
  }

  name = "ingested_data_notification-${var.environment}"
  topic_display_name    = "ingested_data_notification-${var.environment}"
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                          = "${var.project}-${var.environment}-sns-ingested-topic"
  tag_environment                   = var.environment
  tag_contact                       = local.contact
  tag_budgetcode                    = local.budget_code
  tag_owner                         = local.owner
  tag_projectname                   = local.project
  tag_systemtier                    = local.tier
  tag_drtier                        = local.tier
  tag_dataclassification            = local.na
  tag_notes                         = local.na
  tag_eol                           = local.na
  tag_maintwindow                   = local.na
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


module "sns_processed_data" {
  source = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=1.0.0"

  policy_template_vars = {
    topic_name      = "processed_data_notification-${var.environment}"
    region          = var.region
    account_id      = data.aws_caller_identity.account.account_id
    s3_bucket_name  = module.s3_processed_data.bucket_id
  }

  name = "processed_data_notification-${var.environment}"
  topic_display_name    = "processed_data_notification-${var.environment}"
  app_name              = lower(var.project)
  app_environment       = var.environment

  tag_name                         = "${var.project}-${var.environment}-sns-processed-data"
  tag_environment                   = var.environment
  tag_contact                       = local.contact
  tag_budgetcode                    = local.budget_code
  tag_owner                         = local.owner
  tag_projectname                   = local.project
  tag_systemtier                    = local.tier
  tag_drtier                        = local.tier
  tag_dataclassification            = local.na
  tag_notes                         = local.na
  tag_eol                           = local.na
  tag_maintwindow                   = local.na
  tags = {
    Group                               = local.group
    Department                          = local.department
  }
}


#####################################################################
# Datalake - Neptune Cluster                                        #
#####################################################################

# resource "aws_security_group" "lineage" {
#     name        = "Data Lake Lineage"
#     description = "Allow inbound traffic to Neptune"
#     vpc_id      = aws_vpc.datalake.id
#
#     ingress {
#         description = "Gremlin"
#         from_port   = 8182
#         to_port     = 8182
#         protocol    = "tcp"
#         # cidr_blocks = [aws_vpc.development.cidr_block]
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     egress {
#         from_port   = 0
#         to_port     = 0
#         protocol    = "-1"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     tags = merge(local.tags, {Name = "Data Lake Lineage SG"})
# }
#
#
# resource "aws_subnet" "lineage_frontend" {
#     vpc_id            = aws_vpc.datalake.id
#     cidr_block        = "172.31.0.0/24"
#     availability_zone = "us-east-1a"
#
#     tags = merge(local.tags, {Name = "Data Lake Lineage Fronend Subnet"})
# }
#
#
# resource "aws_route_table_association" "lineage_frontend" {
#     subnet_id      = aws_subnet.lineage_frontend.id
#     route_table_id = aws_vpc.datalake.default_route_table_id
# }
#
#
# resource "aws_subnet" "lineage_backend" {
#     vpc_id            = aws_vpc.datalake.id
#     cidr_block        = "172.31.1.0/24"
#     availability_zone = "us-east-1b"
#
#     tags = merge(local.tags, {Name = "Data Lake Lineage Backend Subnet"})
# }
#
#
# resource "aws_route_table_association" "lineage_backend" {
#     subnet_id      = aws_subnet.lineage_backend.id
#     route_table_id = aws_vpc.datalake.default_route_table_id
# }
#
#
# module "lineage_neptune_cluster" {
#     source  = "git::ssh://tf_svc@bitbucket.ama-assn.org:7999/te/terraform-aws-neptune-cluster.git?ref=1.0.0"
#     app_name                          = lower(var.project)
#     instance_id                       = lower(var.project)
#     neptune_subnet_list     = [aws_subnet.lineage_frontend.id, aws_subnet.lineage_backend.id]
#     security_group_ids      = [aws_security_group.lineage.id]
#     environment                       = var.environment
#
#     tag_name                          = "${var.project}-${var.environment}-neptune-cluster"
#     tag_environment                   = var.environment
#     tag_contact                       = local.contact
#     tag_budgetcode                    = local.budget_code
#     tag_owner                         = local.owner
#     tag_projectname                   = local.project
#     tag_systemtier                    = local.tier
#     tag_drtier                        = local.tier
#     tag_dataclassification            = local.na
#     tag_notes                         = local.na
#     tag_eol                           = local.na
#     tag_maintwindow                   = local.na
#     tags = {
#         Group                               = local.group
#         Department                          = local.department
#     }
# }


module "datalabs_terraform_state" {
    source  = "../../Module/DataLake"
    project = "DataLake"
    datanow_version     = "1.0.0"
}
