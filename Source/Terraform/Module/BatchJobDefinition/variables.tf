variable "name" {
  description = "Application Name"
  type        = string
}

variable "project" {
  description = "application project name"
  type        = string
}

variable "environment" {
  description = "deployment environment ID"
  type        = string
}

variable "container_vars" {
  description = "container properties template variables"
  type        = map(string)
  default     = {}
}

variable "policy_vars" {
  description = "container properties template variables"
  type        = map(string)
  default     = {}
}


### Container Properties ###
variable "ecr_account" {
  description = "ECR Account ID"
  type        = string
  default     = "394406051370"
}

variable "image" {
  description = "container image name"
  type        = string
}

variable "image_version" {
  description = "container image version tag"
  type        = string
}

variable "command" {
  description = "job command argument list"
  type        = list(string)
  default     = []
}

variable "environment_vars" {
  description = "AWS Batch job description specific JSON string describing job environment variables"
  type        = string
  default     = "null"
}

variable "volumes" {
  description = "AWS Batch job description specific JSON string describing attached volumes"
  type        = string
  default     = "null"
}

variable "mount_points" {
  description = "AWS Batch job description specific JSON string describing mount points"
  type        = string
  default     = "null"
}

variable "readonly_filesystem" {
  description = "whether the root filesystem should be readonly"
  type        = bool
  default     = true
}

variable "ulimits" {
  description = "AWS Batch job description specific JSON string describing Unix-type user limits"
  type        = string
  default     = "null"
}

variable "user" {
  description = "username to under which the job is run"
  type        = string
  default     = ""
}

variable "resource_requirements" {
  description = "AWS Batch job description specific JSON string describing resource requirements"
  type        = string
  default     = "null"
}

variable "linux_parameters" {
  description = "AWS Batch job description specific JSON string describing linux parameters"
  type        = string
  default     = "null"
}

variable "log_configuration" {
  description = "AWS Batch job description specific JSON string describing the log configuration"
  type        = string
  default     = "null"
}

variable "secrets" {
  description = "job secrets"
  type        = string
  default     = "null"
}


variable "service_role" {
  description = "service/execution role ARN"
  type        = string
}


### tags ###

variable "tag_contact" {
  description = "contact"
  type        = string
  default     = "contact testng"
}

variable "tag_systemtier" {
  description = "system tier"
  type        = string
  default     = "system tier testng"
}

variable "tag_drtier" {
  description = "DR tier"
  type        = string
  default     = "DR tier testng"
}

variable "tag_dataclassification" {
  description = "data classification"
  type        = string
  default     = "data classification testng"
}

variable "tag_budgetcode" {
  description = "budget code"
  type        = string
  default     = "budget code testng"
}

variable "tag_owner" {
  description = "owner"
  type        = string
  default     = "owner testng"
}

variable "tag_notes" {
  description = "notes"
  type        = string
  default     = "notes testng"
}

variable "tag_eol" {
  description = "EOL"
  type        = string
  default     = "EOL tag testng"
}

variable "tag_maintwindow" {
  description = "maintenance window"
  type        = string
  default     = "maint window tag testng"
}

variable "tags" {
  type        = map(string)
  description = "Tags assigned to all capable resources."
  default     = {}
}
