variable "task" {
  type = "string"
}

variable "account" {
  description = "ID of the account in which the job will run"
  type        = string
}

variable "ecr_account" {
  description = "ECR Account ID"
  type        = string
  default     = "394406051370"
}

variable "region" {
  description = "AWS region"
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

variable "vcpus" {
  description = "number of vCPUs reserved for the container"
  type        = number
  default     = 1
}

variable "memory" {
  description = "maximum memory size in MiB available to the job"
  type        = number
  default     = 2048
}

variable "container_properties_vars" {
  type        = map(string)
  description = "Variables to pass to the container properites template"
  default     = {}
}

variable "job_policy_vars" {
  type        = map(string)
  description = "Variables to pass to the job iam policy template"
  default     = {}
}

### tags ###

variable "tag_name" {
  description = "Application Name"
  type        = string
  default     = "name testng"
}

variable "tag_environment" {
  description = "environment"
  type        = string
  default     = "environment testng"
}

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

variable "tag_projectname" {
  description = "project name"
  type        = string
  default     = "project name testng"
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
