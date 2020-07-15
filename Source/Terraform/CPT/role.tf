resource "aws_iam_role" "cpt_lambda_role" {
    name = "DataLabsCPTLambdaExecution"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            }
        }
    ]
}
EOF

    tags = merge(local.tags, {Name = "CPT API Lambda function execution role"})
}


resource "aws_iam_policy" "cpt_lambda_logging" {
    name        = "DataLabsCPTLambdaLogging"
    path        = "/"
    description = "IAM policy for logging from a lambda"

    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_logs" {
    role       = aws_iam_role.cpt_lambda_role.name
    policy_arn = aws_iam_policy.cpt_lambda_logging.arn
}
