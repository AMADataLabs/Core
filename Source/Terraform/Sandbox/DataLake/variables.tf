variable "project" {
    description     = "Name of the project associated with this application stack."
    type            = string
    default         = "DataLake"
}

variable "environment" {
    description     = "Name of the AWS deployment environment."
    type            = string
    default         = "sbx"
}

variable "region" {
    description     = "Name of the AWS deployment region."
    type            = string
    default         = "us-east-1"
}

variable "lambda_code_bucket" {
    description     = "Name of the S3 bucket used to hold Lambda function code artifacts."
    type            = string
    default         = "ama-hsg-datalabs-lambda-code-sandbox"
}


variable "datanow_image" {
    description     = "ECR repository (image name) for the DataNow container image."
    type            = string
    default         = "datanow"
}


variable "datanow_version" {
    description     = "Version number of the DataNow container image."
    type            = string
    default         = "1.0.0"
}
