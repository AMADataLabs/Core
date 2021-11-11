variable "project" {
   description  = "Name of the project used primarily in resource names."
   type = string
   default = "DataLake"
}

variable "contact" {
   description  = "Email of the contact for this app stack."
   type = string
   default = "DataLabs@ama-assn.org"
}

variable "owner" {
   description  = "Name of the owner of this application."
   type = string
   default = "Data Labs"
}

variable "budget_code" {
   description  = "Budget code for accounting purposes."
   type = string
   default = "PBW"
}

variable "accounts" {
   description  = "AWS accounts into which this app stack is deployed."
   default = {
     sbx = "644454719059"
     dev = "191296302136"
     tst = "194221139997"
     stg = "340826698851"
     prd = "285887636563"
   }
}

variable "region" {
   description  = "AWS region into which this app stack is deployed."
   type = string
   default = "us-east-1"
}

variable "days_to_recover" {
   description  = "AWS Secrets Manager Recovery Window in Days"
   type = number
   default = 0
}


#Scheduler Task Definition Variables

variable "scheduler_image_template" {
   description  = "The image name of the container image stored in ECR"
   type = string
   default = "scheduler"
}

variable "scheduler_version" {
   description  = "The version of the image stored in the ECR repository"
   type = string
   default = "1.0.0"
}

variable "dynamodb_config_table_template" {
    description = "timeout in seconds"
    type        = string
    default     = "DataLake-configuration-%%environment%%"
}
