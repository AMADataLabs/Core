### DataNow Parameters ###

resource "aws_ssm_parameter" "datanow_remove_token_url" {
    name  = "${local.parameter_name_prefix}datanow_remove_token_url"
    type  = "String"
    value = "https://${local.datanow_domain}/apiv2/login"

    tags = local.tags
}

resource "aws_ssm_parameter" "datanow_token_url" {
    name  = "${local.parameter_name_prefix}datanow_token_url"
    type  = "String"
    value = "https://${local.datanow_domain}/apiv2/token"

    tags = local.tags
}

resource "aws_ssm_parameter" "datanow_url" {
    name  = "${local.parameter_name_prefix}datanow_url"
    type  = "String"
    value = " https://${local.datanow_domain}"

    tags = local.tags
}

resource "aws_ssm_parameter" "datanow_user_id" {
    name  = "${local.parameter_name_prefix}datanow_user_id"
    type  = "String"
    value = "webapp"

    tags = local.tags
}

resource "aws_ssm_parameter" "datanow_password" {
    name  = "${local.parameter_name_prefix}datanow_password"
    type  = "String"
    value = random_password.datanow_password.result

    tags = local.tags
}
