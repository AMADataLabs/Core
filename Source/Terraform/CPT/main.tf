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
            lambda_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.descriptors}",
            lambda_consumer_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.consumer_descriptor}",
            lambda_consumer_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.consumer_descriptors}",
            lambda_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.clinician_descriptors}",
            lambda_all_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.all_clinician_descriptors}",
            # lambda_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.pla_details}",
            # lambda_all_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.all_pla_details}",
            # lambda_modifier_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.modifier}",
            # lambda_modifiers_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.modifiers}",
            # lambda_latest_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.latest_pdfs}",
            # lambda_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.pdfs}",
            # lambda_releases_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.releases}",
            lambda_return404_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.default}",
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


module "endpoint_descriptor" {
    source = "./endpoint"

    function_name       = "cpt_descriptor_code"
    task_class          = local.task_classes.descriptor
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address


    function_name_TEST  = local.function_names.descriptor
    api_gateway_id_TEST = aws_api_gateway_rest_api.cpt_api_gateway_TEST.id
}


module "endpoint_all_descriptors" {
    source = "./endpoint"

    function_name       = "all_cpt_descriptors"
    task_class          = local.task_classes.descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address


    function_name_TEST   = local.function_names.descriptors
    api_gateway_id_TEST  = aws_api_gateway_rest_api.cpt_api_gateway_TEST.id
}


module "endpoint_consumer_descriptor" {
    source = "./endpoint"

    function_name       = "consumer_descriptor_code"
    task_class          = local.task_classes.consumer_descriptor
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_consumer_descriptors" {
    source = "./endpoint"

    function_name       = "all_consumer_descriptor"
    task_class          = local.task_classes.consumer_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_clinician_descriptors" {
    source = "./endpoint"

    function_name       = "clinician_descriptor_code"
    task_class          = local.task_classes.clinician_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_all_clinician_descriptors" {
    source = "./endpoint"

    function_name       = "all_clinician_descriptor"
    task_class          = local.task_classes.all_clinician_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_pla_details" {
    source = "./endpoint"

    function_name       = "pla_code"
    task_class          = local.task_classes.pla_details
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_all_pla_details" {
    source = "./endpoint"

    function_name       = "all_pla"
    task_class          = local.task_classes.all_pla_details
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_modifier" {
    source = "./endpoint"

    function_name       = "modifier_code"
    task_class          = local.task_classes.modifier
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_modifiers" {
    source = "./endpoint"

    function_name       = "all_modifier"
    task_class          = local.task_classes.modifiers
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


# module "endpoint_latest_pdfs" {
#     source = "./endpoint"

#     function_name       = "latest_pdsf"
#     task_class          = local.task_classes.latest_pdfs
#     region              = local.region
#     account_id          = data.aws_caller_identity.account.account_id
#     role                = aws_iam_role.cpt_lambda_role.arn
#     api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
#     database_name       = aws_db_instance.cpt_api_database.name
#     database_host       = aws_db_instance.cpt_api_database.address
# }


# module "endpoint_pdfs" {
#     source = "./endpoint"

#     function_name       = "all_pdfs"
#     task_class          = local.task_classes.pdfs
#     region              = local.region
#     account_id          = data.aws_caller_identity.account.account_id
#     role                = aws_iam_role.cpt_lambda_role.arn
#     api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
#     database_name       = aws_db_instance.cpt_api_database.name
#     database_host       = aws_db_instance.cpt_api_database.address
# }


# module "endpoint_releases" {
#     source = "./endpoint"

#     function_name       = "all_releases"
#     task_class          = local.task_classes.releases
#     region              = local.region
#     account_id          = data.aws_caller_identity.account.account_id
#     role                = aws_iam_role.cpt_lambda_role.arn
#     api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
#     database_name       = aws_db_instance.cpt_api_database.name
#     database_host       = aws_db_instance.cpt_api_database.address
# }


module "endpoint_default" {
    source = "./endpoint"

    function_name       = "Return404"
    task_class          = local.task_classes.default
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.cpt_lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
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
    task_class_base = "datalabs.access.cpt.api"
    task_classes = {
        descriptor                  = "${local.task_class_base}.descriptor.DescriptorEndpointTask"
        descriptors                 = "${local.task_class_base}.descriptor.AllDescriptorsEndpointTask"
        consumer_descriptor         = "${local.task_class_base}.consumer.descriptor.ConsumerDescriptorEndpointTask"
        consumer_descriptors        = "${local.task_class_base}.consumer.descriptor.AllConsumerDescriptorEndpointTask"
        clinician_descriptors       = "${local.task_class_base}.clinician.descriptor.ClinicianDescriptorsEndpointTask"
        all_clinician_descriptors   = "${local.task_class_base}.clinician.descriptor.AllClinicianDescriptorsEndpointTask"
        modifier                    = "${local.task_class_base}.modifier.ModifierEndpointTask"
        modifiers                   = "${local.task_class_base}.modifier.AllModifiersEndpointTask"
        pla_details                 = "${local.task_class_base}.pla.PLADetailsEndpointTask"
        all_pla_details             = "${local.task_class_base}.pla.AllPLADetailsEndpointTask"
        latest_pdfs                 = "${local.task_class_base}.pdf.LatestPDFsEndpointTask"
        pdfs                        = "${local.task_class_base}.pdf.PDFsEndpointTask"
        releases                    = "${local.task_class_base}.release.ReleasesEndpointTask"
        default                     = "${local.task_class_base}.default.DefaultEndpointTask"
    }
}
