variable "database_password" {}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_kms_key" "cpt" {
    key_id = "alias/DataLabs/CPT"
}
