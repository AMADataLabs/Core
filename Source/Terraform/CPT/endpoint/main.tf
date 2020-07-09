
resource "aws_lambda_function" "endpoint_lambda" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name = var.function_name
    role            = var.role
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = 5
    memory_size     = 1024

    environment {
        variables = {
            TASK_CLASS          = var.task_class
            DATABASE_NAME       = var.database_name
            DATABASE_BACKEND    = var.database_backend
            DATABASE_HOST       = var.database_host
            DATABASE_USERNAME   = data.aws_ssm_parameter.database_username.value
            DATABASE_PASSWORD   = data.aws_ssm_parameter.database_password.value
        }
    }
}


data "aws_ssm_parameter" "database_username" {
    name = "/DataLabs/CPT/RDS/username"
}


data "aws_ssm_parameter" "database_password" {
    name = "/DataLabs/CPT/RDS/password"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}
