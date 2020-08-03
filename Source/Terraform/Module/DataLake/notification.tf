
resource "aws_iam_role" "sns_logging" {
    name = "DataLabsDataLakeLoggingRoleForSNS"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "sns.amazonaws.com"
            }
        }
    ]
}
EOF

    tags = merge(local.tags, {Name = "Data Labs Data Lake SNS logger role"})
}


data "aws_iam_policy" "sns_logging" {
    arn = "arn:aws:iam::aws:policy/service-role/AmazonSNSRole"
}


resource "aws_iam_role_policy_attachment" "sns_logging" {
    role       = aws_iam_role.sns_logging.name
    policy_arn = data.aws_iam_policy.sns_logging.arn
}


resource "aws_sns_topic" "ingestion" {
    name = "IngestionBucketNotification"
    sqs_success_feedback_role_arn       = aws_iam_role.sns_logging.arn
    sqs_failure_feedback_role_arn       = aws_iam_role.sns_logging.arn
    sqs_success_feedback_sample_rate    = 100
    lambda_success_feedback_role_arn    = aws_iam_role.sns_logging.arn
    lambda_failure_feedback_role_arn    = aws_iam_role.sns_logging.arn
    lambda_success_feedback_sample_rate = 100

    tags = merge(local.tags, {Name = "Data Labs Data Lake ingestion bucket notification topic"})
}


resource "aws_sns_topic_policy" "ingestion" {
    arn = aws_sns_topic.ingestion.arn

    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccountSubscribe",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "SNS:Subscribe",
        "SNS:Receive"
      ],
      "Resource": "${aws_sns_topic.ingestion.arn}",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "${data.aws_caller_identity.account.account_id}"
        }
      }
    },
    {
      "Sid": "AllowBucketPublish",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": [
        "SNS:Publish"
      ],
      "Resource": "${aws_sns_topic.ingestion.arn}",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "${aws_s3_bucket.datalake_ingestion_bucket.arn}"
        }
      }
    }
  ]
}
POLICY
}


resource "aws_s3_bucket_notification" "ingestion_sns_notification" {
    bucket = data.aws_ssm_parameter.ingestion_bucket.value

    topic {
        topic_arn           = aws_sns_topic.ingestion.arn
        events              = ["s3:ObjectCreated:*"]
    }
}


resource "aws_sns_topic" "processed" {
    name = "ProcessedBucketNotification"
    sqs_success_feedback_role_arn       = aws_iam_role.sns_logging.arn
    sqs_failure_feedback_role_arn       = aws_iam_role.sns_logging.arn
    sqs_success_feedback_sample_rate    = 100
    lambda_success_feedback_role_arn    = aws_iam_role.sns_logging.arn
    lambda_failure_feedback_role_arn    = aws_iam_role.sns_logging.arn
    lambda_success_feedback_sample_rate = 100

    tags = merge(local.tags, {Name = "Data Labs Data Lake processed bucket notification topic"})
}


resource "aws_sns_topic_policy" "processed" {
    arn = aws_sns_topic.processed.arn

    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccountSubscribe",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "SNS:Subscribe",
        "SNS:Receive"
      ],
      "Resource": "${aws_sns_topic.processed.arn}",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": "${data.aws_caller_identity.account.account_id}"
        }
      }
    },
    {
      "Sid": "AllowBucketPublish",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": [
        "SNS:Publish"
      ],
      "Resource": "${aws_sns_topic.processed.arn}",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "${aws_s3_bucket.datalake_processed_bucket.arn}"
        }
      }
    }
  ]
}
POLICY
}

resource "aws_s3_bucket_notification" "processed_sns_notification" {
    bucket = data.aws_ssm_parameter.processed_bucket.value

    topic {
        topic_arn           = aws_sns_topic.processed.arn
        events              = ["s3:ObjectCreated:*"]
    }
}
