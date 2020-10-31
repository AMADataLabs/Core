data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_acm_certificate" "datanow" {
    domain = "*.amaaws.org"
}
