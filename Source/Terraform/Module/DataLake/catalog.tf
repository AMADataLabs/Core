resource "aws_glue_catalog_database" "datalake" {
    name = lower(var.project)
}

resource "aws_glue_crawler" "datalake" {
    database_name   = aws_glue_catalog_database.datalake.name
    name            = lower(var.project)
    schedule        = "cron(0 0 * * ? *)"
    role            = aws_iam_role.glue_crawler.arn

    s3_target {
        path = "s3://${data.aws_ssm_parameter.ingestion_bucket.value}"
    }

    s3_target {
        path = "s3://${data.aws_ssm_parameter.processed_bucket.value}"
    }

    schema_change_policy {
        delete_behavior     = "DEPRECATE_IN_DATABASE"
        update_behavior     = "UPDATE_IN_DATABASE"
    }

    tags = merge(local.tags, {Name = "Data Lake Glue Crawler"})
}

resource "aws_iam_role" "glue_crawler" {
    name        = "${var.project}GlueCrawler"

    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

    tags = merge(local.tags, {Name = "Data Lake Glue Crawler Role"})
}

resource "aws_iam_policy" "glue_crawler" {
    name = "${var.project}GlueCrawler"

    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "glue:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "logs:*",
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_policy_attachment" "glue_crawler" {
    name        = "${var.project}GlueCrawler"
    roles       = [aws_iam_role.glue_crawler.name]
    policy_arn  = aws_iam_policy.glue_crawler.arn
}
