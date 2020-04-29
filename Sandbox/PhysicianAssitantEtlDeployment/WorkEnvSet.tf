provider "aws" {
  region     = "us-east-1"
  shared_credentials_file = "/Users/elaineyao/.aws/credentials"

}

# TODO List:
# done 2 S3 buckets: input & output
# 2 lambda funtions
# 2 inovation configuration: aws_s3_bucket_notification resource, to link lambda and S3
# 2 aws_lambda_permisson: to grant S3 permission to invoke lambda function
# 1 AWS Glue Crawler
# 1 AWS Glue Database
# 1 AWS Glue ETL
# 4 IAM roles attached to resources to get access: 2 lambda function, 1 crawler, 1 ETL

# Questions: 
# 2. IAM roles parameters set up and assume_role_policy, what's the difference from attach exact policy
# 3. aws_lambada_function: statment_id?
# 4. how to read the lambda function files? put file name on it is enough?

# create 2 S3 buckets:
resource "aws_s3_bucket" "inputbucket" {
  bucket = "pa-data-input-file-test"
  acl    = "private"
}

resource "aws_s3_bucket" "outputbucket" {
  bucket = "pa-data-output-file-csv-test"
  acl    = "private"
}

# create the Glue Database
resource "aws_glue_catalog_database" "database" {
  name = "pa_data_crawler_output-test"
}

# create the 1st lambda function to trigger the crawler
resource "aws_lambda_permission" "crawlertrigger" {
  statement_id  = "AllowExecutionFromS3InputBucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.S3triggerTOGlueCrawlerTest.arn
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::pa-data-input-file-test"
}

resource "aws_lambda_function" "S3triggerTOGlueCrawlerTest" {
  filename      = "lambda_function.zip"
  function_name = "S3triggerTOGlueCrawlerTest"
  role          = aws_iam_role.triggerTOGlueCrawlerTest.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.6"
}

# create the IAM role that attached to 1st lambda function
resource "aws_iam_role" "triggerTOGlueCrawlerTest" {
  name = "triggerTOGlueCrawlerTest"
  tags = {
    DontParkMe         = "True"
    Name               = "triggerTOGlueCrawlerTest"
    Env                = "sandbox"
    Contact            = "na"
    DRTier             = "na"
    DataCalssification = "none"
    BudgetCode         = "IT"
    Owner              = "na"
    Notes              = "na"
    OS                 = "na"
    EOL                = "na"
    MaintenanceWindow  = "na"
  }
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

}

# write the user-defined policy that attached to the lambda function
resource "aws_iam_policy" "lambdapolicytest" {
  name        = "lambdapolicytest"
  description = "Policy for input lambda function"

  policy = <<EOF
{
  "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:us-east-1:644454719059:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:644454719059:log-group:/aws/lambda/S3triggerTOGlueCrawlerTest:*"
            ]
        }
    ]
}
EOF

}

# attach the UDF policy and AWS maanged policy to the lambda function
resource "aws_iam_policy_attachment" "lambdapolicyattachment" {
  name       = "lambdapermissions"
  policy_arn = aws_iam_policy.lambdapolicytest.arn
  # TF-UPGRADE-TODO: In Terraform v0.10 and earlier, it was sometimes necessary to
  # force an interpolation expression to be interpreted as a list by wrapping it
  # in an extra set of list brackets. That form was supported for compatibility in
  # v0.11, but is no longer supported in Terraform v0.12.
  #
  # If the expression in the following list itself returns a list, remove the
  # brackets to avoid interpretation as a list of lists. If the expression
  # returns a single list item then leave it as-is and remove this TODO comment.
  roles = [aws_iam_role.triggerTOGlueCrawlerTest.name]
}

resource "aws_iam_policy_attachment" "lambdapolicyattachmentsecond" {
  name       = "lambdapermissionsaws" 
  policy_arn = "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess"
  roles      = [aws_iam_role.triggerTOGlueCrawlerTest.name]
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = "${aws_s3_bucket.inputbucket.id}"

  lambda_function {
    lambda_function_arn = "${aws_lambda_function.3triggerTOGlueCrawlerTest.arn}"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "AWSLogs/"
    filter_suffix       = ".log"
  }
  depends_on = [
    aws_lambda_permission.crawlertrigger
  ]
}


# create the crawler to crawl data into Database:
resource "aws_glue_crawler" "PhysicianAssistantDataCrawlertest" {
  database_name = aws_glue_catalog_database.database.name
  name          = "PhysicianAssistantDataCrawlertest"
  role          = aws_iam_role.InputPaDatatest.arn

  s3_target {
    path = "s3://${aws_s3_bucket.inputbucket.id}"
  }
}

# IAM role attached to Crawler
resource "aws_iam_role" "InputPaDatatest" {
  name = "InputPaDatatest"
  tags = {
    DontParkMe         = "True"
    Name               = "InputPaDatatest"
    Env                = "sandbox"
    Contact            = "na"
    DRTier             = "na"
    DataCalssification = "none"
    BudgetCode         = "IT"
    Owner              = "na"
    Notes              = "na"
    OS                 = "na"
    EOL                = "na"
    MaintenanceWindow  = "na"
  }
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "glue.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

}

# write the UDF policy that attached to the crawler
resource "aws_iam_policy" "crawlerpolicytest" {
  name        = "crawlerpolicytest"
  description = "Policy for crawler role InputPaData"

  policy = <<EOF
{
   "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::pa-data-input-file-test*"
            ]
        }
    ]
}
EOF

}

# attach the UDF policy and AWS managed policy to the crawler
resource "aws_iam_policy_attachment" "crawlerpolicyattachment" {
  name       = "crawlerpermissions"
  policy_arn = aws_iam_policy.crawlerpolicytest.arn
  roles      = [aws_iam_role.InputPaDatatest.name]
}

resource "aws_iam_policy_attachment" "crawlerpolicyattachmentsecond" {
  name       = "crawlerpermissions"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
  roles      = [aws_iam_role.InputPaDatatest.name]
}

# create lambda function to start Glue ETL, attached with permission and IAM role
resource "aws_lambda_permission" "glueetltrigger" {
  statement_id  = "AllowExecutionFromS3OutputBucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.StartGlueJobtest.arn
  principal     = "s3.amazonaws.com"
  
}

resource "aws_lambda_function" "StartGlueJobtest" {
  filename      = "lambda_function_etl.zip"
  function_name = "StartGlueJobtest"
  role          = aws_iam_role.StartGlueJobtest.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.6"
}

resource "aws_iam_role" "StartGlueJobtest" {
  name = "StartGlueJobtest"
  tags = {
    DontParkMe         = "True"
    Name               = "StartGlueJobtest"
    Env                = "sandbox"
    Contact            = "na"
    DRTier             = "na"
    DataCalssification = "none"
    BudgetCode         = "IT"
    Owner              = "na"
    Notes              = "na"
    OS                 = "na"
    EOL                = "na"
    MaintenanceWindow  = "na"
  }
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow"
        }
    ]
}
EOF

}

resource "aws_iam_policy" "lambdaETLpolicy" {
  name        = "lambdaETLpolicy"
  description = "Policy for lambda etl role"

  policy = <<EOF
{
   "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:us-east-1:644454719059:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:644454719059:log-group:/aws/lambda/StartGlueJobtest:*"
            ]
        }
    ]
}
EOF

}

resource "aws_iam_policy_attachment" "lambdaETLpolicyattachment" {
  name       = "lambdaETLpermissions"
  policy_arn = aws_iam_policy.lambdaETLpolicy.arn
  roles      = [aws_iam_role.StartGlueJobtest.name]
}

variable "managed_policies" {
  default = [
    "arn:aws:iam::aws:policy/AWSGlueConsoleSageMakerNotebookFullAccess",
    "arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchFullAccess",
  ]
}

resource "aws_iam_role_policy_attachment" "lambdaETLmanageattachment" {
  count      = length(var.managed_policies)
  policy_arn = element(var.managed_policies, count.index)
  role       = aws_iam_role.StartGlueJobtest.name
}

# create Glue ETL
resource "aws_glue_job" "AAPA-Merge-Jobtest" {
  name     = "AAPA-Merge-Jobtest"
  role_arn = aws_iam_role.PaETLgluerole.arn
  command {
    script_location = file("/Users/elaineyao/Desktop/AMA/DataEng/TerraformProject/WorkflowAuto/AAPA-Merge-Job.py")
  }
}

resource "aws_iam_role" "PaETLgluerole" {
  name = "PaETLgluerole"
  tags = {
    DontParkMe         = "True"
    Name               = "PaETLgluerole"
    Env                = "sandbox"
    Contact            = "na"
    DRTier             = "na"
    DataCalssification = "none"
    BudgetCode         = "IT"
    Owner              = "na"
    Notes              = "na"
    OS                 = "na"
    EOL                = "na"
    MaintenanceWindow  = "na"
  }
  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "glue.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

}

resource "aws_iam_policy" "PaETLgluepolicy" {
  name        = "PaETLgluepolicy"
  description = "Policy for the PA ETL Job"

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

resource "aws_iam_policy_attachment" "gluepolicyattachment" {
  name       = "gluepermissions${formatdate("DDhmm", timestamp())}"
  policy_arn = aws_iam_policy.PaETLgluepolicy.arn
  roles      = [aws_iam_role.PaETLgluerole.name]
}

