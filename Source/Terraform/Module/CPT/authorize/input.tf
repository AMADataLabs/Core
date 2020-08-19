variable "project" {
    description     = "Project name used in names to distinguish resources."
    type            = string
}

variable "function_name" {
    description = "AWS region"
    type        = string
}


variable "task_class" {
    description = "task class name"
    type        = string
}


variable "region" {
    description = "AWS region"
    type        = string
}


variable "account_id" {
    description = "AWS Account ID"
    type        = string
}


variable "role" {
    description = "Lambda function role"
    type        = string
}


variable "api_gateway_id" {
    description = "API Gateway ID"
    type        = string
}


variable "passport_url" {
	description = "Passport Url"
	type        = string
}
