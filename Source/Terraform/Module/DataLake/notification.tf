# resource "aws_iam_role" "sns_logging" {
#     name = "DataLabs${var.project}LoggingRoleForSNS"
#
#     assume_role_policy = <<EOF
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": "sts:AssumeRole",
#             "Principal": {
#                 "Service": "sns.amazonaws.com"
#             }
#         }
#     ]
# }
# EOF
#
#     tags = merge(local.tags, {Name = "Data Labs Data Lake SNS logger role"})
# }
#
#
# data "aws_iam_policy" "sns_logging" {
#     arn = "arn:aws:iam::aws:policy/service-role/AmazonSNSRole"
# }
#
#
# resource "aws_iam_role_policy_attachment" "sns_logging" {
#     role       = aws_iam_role.sns_logging.name
#     policy_arn = data.aws_iam_policy.sns_logging.arn
# }
#
#
# module "ingested_data_sns_topic" {
#     source                  = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=feature/sns-updates"
#     name                    = "IngestedDataNotification"
#     topic_display_name            = "IngestedDataNotification"
#     app_name                = "datalake"
#     app_environment         = lower(local.tags["Env"])
#     sqs_success_feedback_sample_rate    = 100
#     lambda_success_feedback_sample_rate = 100
#
#     policy_template         = file("policies/s3_notification_topic.json")
#     policy_template_vars    = {
#         topic_name      = "IngestedDataNotification"
#         region          = "us-east-1"
#         account_id      = data.aws_caller_identity.account.account_id
#         s3_bucket_name  = data.aws_ssm_parameter.ingested_data_bucket.value
#     }
#
#     tag_name                = "${var.project} ingested data bucket notification topic"
#     tag_environment         = local.tags["Env"]
#     tag_contact             = local.tags["Contact"]
#     tag_systemtier          = local.tags["SystemTier"]
#     tag_drtier              = local.tags["DRTier"]
#     tag_dataclassification  = local.tags["DataClassification"]
#     tag_budgetcode          = local.tags["BudgetCode"]
#     tag_owner               = local.tags["Owner"]
#     tag_projectname         = var.project
#     tag_notes               = ""
#     tag_eol                 = local.tags["EOL"]
#     tag_maintwindow         = local.tags["MaintenanceWindow"]
# }
#
#
# resource "aws_s3_bucket_notification" "ingested_data_sns_notification" {
#     bucket = data.aws_ssm_parameter.ingested_data_bucket.value
#
#     topic {
#         topic_arn           = module.ingested_data_sns_topic.this_sns_topic_arn
#         events              = ["s3:ObjectCreated:*"]
#     }
# }
#
#
# module "processed_data_sns_topic" {
#     source                  = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-sns.git?ref=feature/sns-updates"
#     name                    = "ProcessedDataNotification"
#     topic_display_name            = "ProcessedDataNotification"
#     app_name                = "datalake"
#     app_environment         = lower(local.tags["Env"])
#     sqs_success_feedback_sample_rate    = 100
#     lambda_success_feedback_sample_rate = 100
#
#     policy_template         = file("policies/s3_notification_topic.json")
#     policy_template_vars    = {
#         topic_name      = "ProcessedDataNotification"
#         region          = "us-east-1"
#         account_id      = data.aws_caller_identity.account.account_id
#         s3_bucket_name  = data.aws_ssm_parameter.processed_data_bucket.value
#     }
#
#     tag_name                = "${var.project} processed data bucket notification topic"
#     tag_environment         = local.tags["Env"]
#     tag_contact             = local.tags["Contact"]
#     tag_systemtier          = local.tags["SystemTier"]
#     tag_drtier              = local.tags["DRTier"]
#     tag_dataclassification  = local.tags["DataClassification"]
#     tag_budgetcode          = local.tags["BudgetCode"]
#     tag_owner               = local.tags["Owner"]
#     tag_projectname         = var.project
#     tag_notes               = ""
#     tag_eol                 = local.tags["EOL"]
#     tag_maintwindow         = local.tags["MaintenanceWindow"]
# }
#
#
# resource "aws_s3_bucket_notification" "processed_data_sns_notification" {
#     bucket = data.aws_ssm_parameter.processed_data_bucket.value
#
#     topic {
#         topic_arn           = module.processed_data_sns_topic.this_sns_topic_arn
#         events              = ["s3:ObjectCreated:*"]
#     }
# }
