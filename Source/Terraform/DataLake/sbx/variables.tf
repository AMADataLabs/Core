variable "create_neptune" {
  description = "Set to true to create the lambda resourc based policy (invoke policy)"
  type        = bool
  default     = false
}

variable "days_to_recover" {
  description = "AWS Secrets Manager Recovery Window in Days"
  type        = number
  default     = 0
}


#Task Definition Variables

variable "datanow_image_prefix" {
  description = "The image name prefix of the container image stored in ECR"
  type        = string
  default     = "datanow"
}

variable "datanow_version" {
  description = "The version of the image stored in the ECR repository"
  type        = string
  default     = "1.1.0"
}

variable "datanow_host_prefix" {
  description = "Host name prefix for DataNow"
  type        = string
  default     = "datanow"
}

variable "s3_lambda_bucket_base_name" {
  description = "Base name of the S3 bucket where Lambda function code artifacts are stored."
  type        = string
  default     = "lambda"
}

variable "s3_data_base_path" {
  description = "Base path in the Data Lake S3 bucket where CPT API data is located."
  type        = string
  default     = "AMA/CPT"
}

variable "public_certificate_arn" {
  description = "ARN of certificate for AMA-wide CNAME"
  type        = string
  default     = "arn:aws:acm:us-east-1:644454719059:certificate/e3976dc3-ad98-4303-b357-557e364ae3ce"
}

variable "host_suffixes" {
  description = "Host name suffixes by environment."
  default = {
    sbx = "-sbx"
    dev = "-dev"
    tst = "-test"
    stg = "-stg"
    itg = "-intg"
    prd = ""
  }
}

variable "domain" {
  description = "Base domain name for public CNAMEs"
  type        = string
  default     = "amaaws.org"
}
