resource "aws_db_instance" "cpt_api_database" {
    identifier                    = local.rds_instance_name
    instance_class                = var.rds_instance_class
    storage_type                  = var.rds_storage_type
    port                          = local.rds_port
    name                          = local.database_name
    allocated_storage             = 20
    engine                        = local.rds_engine
    engine_version                = "11.10"
    parameter_group_name          = "default.postgres11"
    max_allocated_storage         = 1000
    publicly_accessible           = true
    copy_tags_to_snapshot         = true
    performance_insights_enabled  = true
    skip_final_snapshot           = true
    username                      = local.database_username
    password                      = local.database_password

    tags = merge(local.tags, {Name = "${var.project} API Database"})
}


resource "aws_api_gateway_rest_api" "cpt_api_gateway" {
    name = "${var.project} API"
    description = local.spec_description
    body = templatefile(
        "${path.module}/../../../../Build/CPT/api.yaml",
        {
            title = "${var.project} API",
            description = local.spec_description,
            region = local.region,
            project = var.project,
            account_id = data.aws_caller_identity.account.account_id,
            authorizer_uri = module.authorizer_lambda.function_invoke_arn
        }
    )

    tags = merge(local.tags, {Name = "${var.project} API Gateway"})
}


resource "aws_api_gateway_deployment" "cpt_api_deployment_test" {
  depends_on = [aws_api_gateway_rest_api.cpt_api_gateway]

  rest_api_id = aws_api_gateway_rest_api.cpt_api_gateway.id
  stage_name  = "test"

  triggers = {
    redeployment = sha1(join(",", list(
      jsonencode(aws_api_gateway_rest_api.cpt_api_gateway),
      aws_iam_role.lambda_role.arn
    )))
  }

  lifecycle {
    create_before_destroy = true
  }
}


module "endpoint_descriptor" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.descriptor
    task_class          = local.task_classes.descriptor
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_all_descriptors" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.descriptors
    task_class          = local.task_classes.descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_consumer_descriptor" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.consumer_descriptor
    task_class          = local.task_classes.consumer_descriptor
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_consumer_descriptors" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.consumer_descriptors
    task_class          = local.task_classes.consumer_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_clinician_descriptors" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.clinician_descriptors
    task_class          = local.task_classes.clinician_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_all_clinician_descriptors" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.all_clinician_descriptors
    task_class          = local.task_classes.all_clinician_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_pla_details" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.pla_details
    task_class          = local.task_classes.pla_details
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_all_pla_details" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.all_pla_details
    task_class          = local.task_classes.all_pla_details
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_modifier" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.modifier
    task_class          = local.task_classes.modifier
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_modifiers" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.modifiers
    task_class          = local.task_classes.modifiers
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_latest_pdfs" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.latest_pdfs
    task_class          = local.task_classes.latest_pdfs
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


# module "endpoint_pdfs" {
#     source = "./endpoint"

#     project             = var.project
#     function_name       = local.function_names.pdfs
#     task_class          = local.task_classes.pdfs
#     region              = local.region
#     account_id          = data.aws_caller_identity.account.account_id
#     role                = aws_iam_role.lambda_role.arn
#     api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
#     database_host       = aws_db_instance.cpt_api_database.address
# }


module "endpoint_releases" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.releases
    task_class          = local.task_classes.releases
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "endpoint_default" {
    source = "./endpoint"

    project             = var.project
    function_name       = local.function_names.default
    task_class          = local.task_classes.default
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_arn     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "authorizer_lambda" {
    # source                = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git"
    source              = "git::ssh://git@bitbucket.ama-assn.org:7999/te/terraform-aws-lambda.git?ref=feature/conditional_updates"
    function_name       = local.function_names.authorizer
    s3_lambda_bucket    = data.aws_ssm_parameter.lambda_code_bucket.value
    s3_lambda_key       = "CPT/CPT.zip"
    handler             = "awslambda.handler"
    runtime             = local.runtime
    create_alias        = false
    memory_size         = 1024
    timeout             = 5

    lambda_name         = local.function_names.authorizer
    lambda_policy_vars  = {
        account_id                  = data.aws_caller_identity.account.account_id
        region                      = local.region
        project                     = var.project
    }

    create_lambda_permission    = false
    api_arn                     = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}"

    environment_variables = {
        variables = {
            TASK_WRAPPER_CLASS      = "datalabs.access.authorize.awslambda.AuthorizerLambdaTaskWrapper"
            TASK_CLASS              = local.task_classes.authorizer
            PASSPORT_URL            = data.aws_ssm_parameter.passport_url.arn
        }
    }

    tag_name                = "${var.project} API Authorizer Lambda Function"
    tag_environment         = local.tags["Env"]
    tag_contact             = local.tags["Contact"]
    tag_systemtier          = local.tags["SystemTier"]
    tag_drtier              = local.tags["DRTier"]
    tag_dataclassification  = local.tags["DataClassification"]
    tag_budgetcode          = local.tags["BudgetCode"]
    tag_owner               = local.tags["Owner"]
    tag_projectname         = var.project
    tag_notes               = ""
    tag_eol                 = local.tags["EOL"]
    tag_maintwindow         = local.tags["MaintenanceWindow"]
}

resource "aws_lambda_permission" "lambda_permission" {
  statement_id  = "AllowAPIInvokefor-${local.function_names.authorizer}"
  action        = "lambda:InvokeFunction"
  function_name = local.function_names.authorizer
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn = "arn:aws:execute-api:${local.region}:${data.aws_caller_identity.account.account_id}:${aws_api_gateway_rest_api.cpt_api_gateway.id}/*/*"
  depends_on = [ module.authorizer_lambda ]
}

module "etl_convert" {
    source = "./etl"

    project             = var.project
    function_name           = local.function_names.convert
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    parent_function         = aws_lambda_function.ingestion_etl_router

    variables               = {
        EXTRACTOR__TASK_CLASS       = "datalabs.etl.cpt.ingest.extract.CPTTextDataExtractorTask"
        EXTRACTOR__INCLUDE_NAMES    = "True"
        EXTRACTOR__BUCKET           = data.aws_ssm_parameter.ingestion_bucket.arn
        EXTRACTOR__BASE_PATH        = data.aws_ssm_parameter.s3_base_path.arn
        EXTRACTOR__FILES            = data.aws_ssm_parameter.raw_data_files.arn
        EXTRACTOR__SCHEDULE         = data.aws_ssm_parameter.release_schedule.arn

        TRANSFORMER__TASK_CLASS     = "datalabs.etl.parse.transform.ParseToCSVTransformerTask"
        TRANSFORMER__PARSERS        = data.aws_ssm_parameter.raw_data_parsers.arn

        LOADER__TASK_CLASS          = "datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask"
        LOADER__BUCKET              = data.aws_ssm_parameter.processed_bucket.arn
        LOADER__FILES               = data.aws_ssm_parameter.converted_data_files.arn
        LOADER__BASE_PATH           = data.aws_ssm_parameter.s3_base_path.arn
    }
}


module "etl_bundle_pdf" {
    source = "./etl"

    project             = var.project
    function_name           = local.function_names.bundlepdf
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    parent_function         = aws_lambda_function.ingestion_etl_router

    variables               = {
        EXTRACTOR__TASK_CLASS           = "datalabs.etl.s3.extract.S3FileExtractorTask"
        EXTRACTOR__INCLUDE_NAMES        = "True"
        EXTRACTOR__BUCKET               = data.aws_ssm_parameter.ingestion_bucket.arn
        EXTRACTOR__BASE_PATH            = data.aws_ssm_parameter.s3_base_path.arn
        EXTRACTOR__FILES                = data.aws_ssm_parameter.pdf_files.arn

        TRANSFORMER__TASK_CLASS         = "datalabs.etl.archive.transform.ZipTransformerTask"

        LOADER__TASK_CLASS              = "datalabs.etl.s3.load.S3FileLoaderTask"
        LOADER__BUCKET                  = data.aws_ssm_parameter.processed_bucket.arn
        LOADER__BASE_PATH               = data.aws_ssm_parameter.s3_base_path.arn
        LOADER__FILES                   = "pdfs.zip"
    }
}


module "etl_load" {
    source = "./etl"

    project             = var.project
    function_name           = local.function_names.loaddb
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    parent_function         = aws_lambda_function.processed_etl_router
    timeout                 = 300

    variables               = {
        EXTRACTOR__TASK_CLASS           = "datalabs.etl.s3.extract.S3UnicodeTextFileExtractorTask"
        EXTRACTOR__INCLUDE_NAMES        = "True"
        EXTRACTOR__BUCKET               = data.aws_ssm_parameter.processed_bucket.arn
        EXTRACTOR__BASE_PATH            = data.aws_ssm_parameter.s3_base_path.arn
        EXTRACTOR__FILES                = data.aws_ssm_parameter.raw_csv_files.arn

        TRANSFORMER__TASK_CLASS         = "datalabs.etl.cpt.api.transform.CSVToRelationalTablesTransformerTask"
        TRANSFORMER__DATABASE_HOST      = aws_db_instance.cpt_api_database.address
        TRANSFORMER__DATABASE_SECRET    = data.aws_secretsmanager_secret.database.arn

        LOADER__TASK_CLASS              = "datalabs.etl.cpt.api.load.CPTRelationalTableLoaderTask"
        LOADER__DATABASE_HOST           = aws_db_instance.cpt_api_database.address
        LOADER__DATABASE_SECRET         = data.aws_secretsmanager_secret.database.arn
    }
}


locals {
    aws_environment = data.aws_ssm_parameter.account_environment.value
    contact = data.aws_ssm_parameter.contact.value
    budget_code = "PBW"
    project = "CPT"
    runtime = "python3.7"
    lambda_code_bucket = data.aws_ssm_parameter.lambda_code_bucket.value
    lambda_code_key = "${local.project}/${local.project}.zip"
    region              = "us-east-1"
    spec_title          = "${var.project} API"
    spec_description    = "${var.project} API Phase I"
    na                  = "N/A"
    owner               = "DataLabs"
    database_secret     = jsondecode(data.aws_secretsmanager_secret_version.database.secret_string)
    rds_instance_name   = local.database_secret["dbinstanceIdentifier"]
    rds_engine          = local.database_secret["engine"]
    rds_port          = local.database_secret["port"]
    database_name       = local.database_secret["dbname"]
    database_username   = local.database_secret["username"]
    database_password   = local.database_secret["password"]
    tags = {
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = "Application"
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Project             = var.project
        Department          = "HSG"
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
    function_names = {
        descriptor                  = "${var.project}GetDescriptor"
        descriptors                 = "${var.project}GetDescriptors"
        consumer_descriptor         = "${var.project}GetConsumerDescriptor"
        consumer_descriptors        = "${var.project}GetConsumerDescriptors"
        clinician_descriptors       = "${var.project}GetClinicianDescriptors"
        all_clinician_descriptors   = "${var.project}GetAllClinicianDescriptors"
        pla_details                 = "${var.project}GetPLADetails"
        all_pla_details             = "${var.project}GetAllPLADetails"
        modifier                    = "${var.project}GetModifier"
        modifiers                   = "${var.project}GetModifiers"
        latest_pdfs                 = "${var.project}GetLatestPDFs"
        pdfs                        = "${var.project}GetPDFs"
        releases                    = "${var.project}GetReleases"
        default                     = "${var.project}Default"
        convert                     = "${var.project}Convert"
        loaddb                      = "${var.project}Load"
        bundlepdf                   = "${var.project}BundlePDF"
        ingestion_etl_router        = "${var.project}IngestionRouter"
        processed_etl_router        = "${var.project}ProcessedRouter"
        authorizer                  = "${var.project}Authorizer"
    }
    task_classes = {
        descriptor                  = "datalabs.access.cpt.api.descriptor.DescriptorEndpointTask"
        descriptors                 = "datalabs.access.cpt.api.descriptor.AllDescriptorsEndpointTask"
        consumer_descriptor         = "datalabs.access.cpt.api.consumer_descriptor.ConsumerDescriptorEndpointTask"
        consumer_descriptors        = "datalabs.access.cpt.api.consumer_descriptor.AllConsumerDescriptorsEndpointTask"
        clinician_descriptors       = "datalabs.access.cpt.api.clinician_descriptor.ClinicianDescriptorsEndpointTask"
        all_clinician_descriptors   = "datalabs.access.cpt.api.clinician_descriptor.AllClinicianDescriptorsEndpointTask"
        modifier                    = "datalabs.access.cpt.api.modifier.ModifierEndpointTask"
        modifiers                   = "datalabs.access.cpt.api.modifier.AllModifiersEndpointTask"
        pla_details                 = "datalabs.access.cpt.api.pla.PLADetailsEndpointTask"
        all_pla_details             = "datalabs.access.cpt.api.pla.AllPLADetailsEndpointTask"
        latest_pdfs                 = "datalabs.access.cpt.api.pdf.LatestPDFsEndpointTask"
        pdfs                        = "datalabs.access.cpt.api.pdf.PDFsEndpointTask"
        releases                    = "datalabs.access.cpt.api.release.ReleasesEndpointTask"
        default                     = "datalabs.access.cpt.api.default.DefaultEndpointTask"
        authorizer                  = "datalabs.access.authorize.task.AuthorizerTask"
    }
}
