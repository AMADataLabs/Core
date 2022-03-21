variable "name" {
  description = "name of the job"
  type        = string
}

variable "environment" {
  description = "ID of the account in which the job will run"
  type        = string
}

variable "security_groups" {
  description = "IDs for the security groups to which the Batch compute environment belongs"
  type        = list(string)
}

variable "subnets" {
  description = "IDs for the subnets to which the Batch compute environment belongs"
  type        = list(string)
}

variable "max_vcpus" {
  description = "Maximum number of vcpus to allow"
  type        = number
  default     = 2
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
