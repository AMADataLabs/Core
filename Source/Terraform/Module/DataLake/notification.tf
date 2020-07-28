resource "aws_sns_topic" "ingestion" {
    name = "IngestionBucketNotification"
}


resource "aws_sns_topic_policy" "ingestion" {
    arn = aws_sns_topic.ingestion.arn

    policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[{
        "Effect": "Allow",
        "Principal": {"AWS":"*"},
        "Action": "SNS:Publish",
        "Resource": "arn:aws:sns:*:*:IngestionBucketNotification",
        "Condition":{
            "ArnLike":{"aws:SourceArn":"${aws_s3_bucket.datalake_ingestion_bucket.arn}"}
        }
    }]
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
}


resource "aws_sns_topic_policy" "processed" {
    arn = aws_sns_topic.processed.arn

    policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[{
        "Effect": "Allow",
        "Principal": {"AWS":"*"},
        "Action": "SNS:Publish",
        "Resource": "arn:aws:sns:*:*:ProcessedBucketNotification",
        "Condition":{
            "ArnLike":{"aws:SourceArn":"${aws_s3_bucket.datalake_processed_bucket.arn}"}
        }
    }]
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
