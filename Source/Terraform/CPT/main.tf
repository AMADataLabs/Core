provider "aws" {
    region = "us-east-1"
}

resource "aws_db_instance" "cpt_api_database" {
    identifier                    = "database-test-ui"  # FIXME: change to "datalabs-api-backend"
    name                          = "sample"
    instance_class                = "db.t2.micro"
    allocated_storage             = 20
    storage_type                  = "gp2"
    engine                        = "postgres"
    engine_version                = "11.5"
    parameter_group_name          = "default.postgres11"
    max_allocated_storage         = 1000
    publicly_accessible           = true
    copy_tags_to_snapshot         = true
    performance_insights_enabled  = true
    skip_final_snapshot           = true
    username                      = data.aws_ssm_parameter.database_username.value
    password                      = data.aws_ssm_parameter.database_password.value

    tags = merge(local.tags, {Name = "CPT API Database"})
}


resource "aws_iam_role" "cpt_lambda_role" {
    name = "DataLabsCPTLambdaExecution"

    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow"
        }
    ]
}
EOF

    tags = merge(local.tags, {Name = "CPT API Lambda function execution role"})
}


resource "aws_lambda_function" "cpt_get_descriptor" {
    s3_bucket       = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_key          = "CPT/CPT.zip"
    function_name   = "CPTGetDescriptor"
    role            = aws_iam_role.cpt_lambda_role.arn
    handler         = "awslambda.handler"
    runtime         = "python3.7"
    timeout         = 5
    memory_size     = 1024

    environment {
        variables = {
            TASK_CLASS="datalabs.access.cpt.api.cpt_descriptor_code.DescriptorEndpointTask"
            DATABASE_NAME=aws_db_instance.cpt_api_database.name
            DATABASE_BACKEND="postgresql+psycopg2"
            DATABASE_HOST=aws_db_instance.cpt_api_database.address
            DATABASE_USERNAME=data.aws_ssm_parameter.database_username.value
            DATABASE_PASSWORD=data.aws_ssm_parameter.database_password.value
        }
    }
}


resource "aws_api_gateway_rest_api" "cpt_api_gateway_TEST" {
    name = "CPT API TEST"
    description = local.spec_description
    body = templatefile(
        "${path.module}/../../../Build/CPT/api.yaml",
        {
            title = "CPT API TEST",
            description = local.spec_description,
            region = local.region,
            lambda_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.descriptor}",
            lambda_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_cpt_descriptors",
            lambda_consumer_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:consumer_descriptor_code",
            lambda_consumer_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_consumer_descriptor",
            lambda_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:clinician_descriptor_code",
            lambda_all_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_clinician_descriptor",
            # lambda_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:pla_details_code",
            # lambda_all_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_pla_details",
            # lambda_modifier_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:modifier_code",
            # lambda_modifiers_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_modifiers",
            # lambda_latest_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:latest_pdfs",
            # lambda_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:pdfs_release",
            # lambda_releases_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_releases",
            lambda_return404_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:Return404",
        }
    )

    tags = merge(local.tags, {Name = "CPT API Gateway"})
}

resource "aws_api_gateway_deployment" "cpt_api_deployment_test_TEST" {
  depends_on = [aws_api_gateway_rest_api.cpt_api_gateway_TEST]

  rest_api_id = aws_api_gateway_rest_api.cpt_api_gateway_TEST.id
  stage_name  = "test"

  triggers = {
    redeployment = sha1(join(",", list(
      jsonencode(aws_api_gateway_rest_api.cpt_api_gateway_TEST),
    )))
  }

  lifecycle {
    create_before_destroy = true
  }
}


# resource "aws_lambda_function" "ConvertCPT_test" {
#     filename        = "../../../Build/CPT/app.zip"
#     function_name   = "ConvertCPT"
#     role            = aws_iam_role.cpt_lambda_role.arn
#     handler         = "datalabs.etl.run.lambda_handler"
#     runtime         = "python3.7"
#     environment {
#         variables = {
#             ETL_CONVERTCPT_LAMBDA_FUNCTION=data.aws_ssm_parameter.ETL_CONVERTCPT_LAMBDA_FUNCTION.value
#             ETL_CONVERTCPT_APP=data.aws_ssm_parameter.ETL_CONVERTCPT_APP.value
#             ETL_CONVERTCPT_EXTRACTOR=data.aws_ssm_parameter.ETL_CONVERTCPT_EXTRACTOR.value
#             ETL_CONVERTCPT_EXTRACTOR_BUCKET=data.aws_ssm_parameter.ETL_CONVERTCPT_EXTRACTOR_BUCKET.value
#             ETL_CONVERTCPT_EXTRACTOR_BASE_PATH=data.aws_ssm_parameter.ETL_CONVERTCPT_EXTRACTOR_BASE_PATH.value
#             ETL_CONVERTCPT_EXTRACTOR_FILES=data.aws_ssm_parameter.ETL_CONVERTCPT_EXTRACTOR_FILES.value
#             ETL_CONVERTCPT_TRANSFORMER=data.aws_ssm_parameter.ETL_CONVERTCPT_TRANSFORMER.value
#             ETL_CONVERTCPT_TRANSFORMER_PARSERS=data.aws_ssm_parameter.ETL_CONVERTCPT_TRANSFORMER_PARSERS.value
#             ETL_CONVERTCPT_LOADER=data.aws_ssm_parameter.ETL_CONVERTCPT_LOADER.value
#             ETL_CONVERTCPT_LOADER_BUCKET=data.aws_ssm_parameter.ETL_CONVERTCPT_LOADER_BUCKET.value
#             ETL_CONVERTCPT_LOADER_FILES=data.aws_ssm_parameter.ETL_CONVERTCPT_LOADER_FILES.value
#             ETL_CONVERTCPT_LOADER_BASE_PATH=data.aws_ssm_parameter.ETL_CONVERTCPT_LOADER_BASE_PATH.value

#             # TODO: These need to be moved to the RDS loading ETL Lambda resource
#             ETL_LOADCPT_LAMBDA_FUNCTION=data.aws_ssm_parameter.ETL_LOADCPT_LAMBDA_FUNCTION.value
#             ETL_LOADCPT_APP=data.aws_ssm_parameter.ETL_LOADCPT_APP.value
#             ETL_LOADCPT_EXTRACTOR=data.aws_ssm_parameter.ETL_LOADCPT_EXTRACTOR.value
#             ETL_LOADCPT_EXTRACTOR_BUCKET=data.aws_ssm_parameter.ETL_LOADCPT_EXTRACTOR_BUCKET.value
#             ETL_LOADCPT_EXTRACTOR_BASE_PATH=data.aws_ssm_parameter.ETL_LOADCPT_EXTRACTOR_BASE_PATH.value
#             ETL_LOADCPT_EXTRACTOR_FILES=data.aws_ssm_parameter.ETL_LOADCPT_EXTRACTOR_FILES.value
#             ETL_LOADCPT_TRANSFORMER=data.aws_ssm_parameter.ETL_LOADCPT_TRANSFORMER.value
#             ETL_LOADCPT_LOADER=data.aws_ssm_parameter.ETL_LOADCPT_LOADER.value
#         }
#     }
# }


resource "aws_api_gateway_rest_api" "cpt_api_gateway" {
    name = local.spec_title
    description = local.spec_description
    body = templatefile(
        "${path.module}/../../../Build/CPT/api.yaml",
        {
            title = local.spec_title,
            description = local.spec_description,
            region = local.region,
            lambda_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:cpt_descriptor_code",
            lambda_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_cpt_descriptors",
            lambda_consumer_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:consumer_descriptor_code",
            lambda_consumer_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_consumer_descriptor",
            lambda_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:clinician_descriptor_code",
            lambda_all_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_clinician_descriptor",
            # lambda_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:pla_details_code",
            # lambda_all_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_pla_details",
            # lambda_modifier_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:modifier_code",
            # lambda_modifiers_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_modifiers",
            # lambda_latest_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:latest_pdfs",
            # lambda_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:pdfs_release",
            # lambda_releases_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:all_releases",
            lambda_return404_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:Return404",
        }
    )

    tags = merge(local.tags, {Name = "CPT API Gateway"})
}


resource "aws_api_gateway_deployment" "cpt_api_deployment_test" {
  depends_on = [aws_api_gateway_rest_api.cpt_api_gateway]

  rest_api_id = aws_api_gateway_rest_api.cpt_api_gateway.id
  stage_name  = "test"

  triggers = {
    redeployment = sha1(join(",", list(
      jsonencode(aws_api_gateway_rest_api.cpt_api_gateway),
    )))
  }

  lifecycle {
    create_before_destroy = true
  }
}


module "lambda_descriptor" {
    source = "./lambda"

    function_name   = "cpt_descriptor_code"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id


    function_name_TEST   = local.function_names.descriptor
    api_gateway_id_TEST  = aws_api_gateway_rest_api.cpt_api_gateway_TEST.id
}


module "lambda_all_descriptors" {
    source = "./lambda"

    function_name   = "all_cpt_descriptors"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_consumer_descriptor" {
    source = "./lambda"

    function_name   = "consumer_descriptor_code"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_consumer_descriptors" {
    source = "./lambda"

    function_name   = "all_consumer_descriptor"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_clinician_descriptors" {
    source = "./lambda"

    function_name   = "clinician_descriptor_code"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_all_clinician_descriptors" {
    source = "./lambda"

    function_name   = "all_clinician_descriptor"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_pla_details" {
    source = "./lambda"

    function_name   = "pla_code"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_all_pla_details" {
    source = "./lambda"

    function_name   = "all_pla"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_modifier" {
    source = "./lambda"

    function_name   = "modifier_code"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "lambda_modifiers" {
    source = "./lambda"

    function_name   = "all_modifier"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


# module "lambda_latest_pdfs" {
#     source = "./lambda"

#     function_name   = "latest_pdsf"
#     region          = local.region
#     account_id      = data.aws_caller_identity.account.account_id
#     api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
# }


# module "lambda_pdfs" {
#     source = "./lambda"

#     function_name   = "all_pdfs"
#     region          = local.region
#     account_id      = data.aws_caller_identity.account.account_id
#     api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
# }


# module "lambda_releases" {
#     source = "./lambda"

#     function_name   = "all_releases"
#     region          = local.region
#     account_id      = data.aws_caller_identity.account.account_id
#     api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
# }


module "lambda_default" {
    source = "./lambda"

    function_name   = "Return404"
    region          = local.region
    account_id      = data.aws_caller_identity.account.account_id
    api_gateway_id  = aws_api_gateway_rest_api.cpt_api_gateway.id
}


data "aws_caller_identity" "account" {}


data "aws_ssm_parameter" "database_username" {
    name = "/DataLabs/CPT/RDS/username"
}


data "aws_ssm_parameter" "database_password" {
    name = "/DataLabs/CPT/RDS/password"
}


data "aws_ssm_parameter" "account_environment" {
    name = "/DataLabs/account_environment"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "lambda_code_bucket" {
    name = "/DataLabs/lambda_code_bucket"
}




locals {
    region              = "us-east-1"
    spec_title          = "CPT API"
    spec_description    = "CPT API Phase I"
    na                  = "N/A"
    tags = {
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = "Application"
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = "PBW"
        Owner               = "Data Labs"
        Notes               = ""
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
    function_names = {
        descriptor                  = "CPTGetDescriptor"
        descriptors                 = "CPTGetDescriptors"
        consumer_descriptor         = "CPTGetConsumerDescriptor"
        consumer_descriptors        = "CPTGetConsumerDescriptors"
        clinician_descriptors       = "CPTGetClinicianDescriptors"
        all_clinician_descriptors   = "CPTGetAllClinicianDescriptors"
        modifier                    = "CPTGetModifier"
        modifiers                   = "CPTGetModifiers"
        pla_details                 = "CPTGetPLADetails"
        all_pla_details             = "CPTGetAllPLADetails"
        latest_pdfs                 = "CPTGetLatestPDFs"
        pdfs                        = "CPTGetPDFs"
        releases                    = "CPTGetReleases"
        default                     = "Return404"
    }
}
