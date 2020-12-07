resource "aws_db_instance" "cpt_api_database" {
    identifier                    = local.rds_instance_name
    instance_class                = var.rds_instance_class
    storage_type                  = var.rds_storage_type
    port                          = local.rds_port
    name                          = local.database_name
    allocated_storage             = 20
    engine                        = local.rds_engine
    engine_version                = "11.8"
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
            lambda_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.descriptor}",
            lambda_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.descriptors}",
            lambda_consumer_descriptor_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.consumer_descriptor}",
            lambda_consumer_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.consumer_descriptors}",
            lambda_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.clinician_descriptors}",
            lambda_all_clinician_descriptors_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.all_clinician_descriptors}",
            lambda_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.pla_details}",
            lambda_all_pla_details_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.all_pla_details}",
            lambda_modifier_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.modifier}",
            lambda_modifiers_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.modifiers}",
            lambda_latest_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.latest_pdfs}",
            # lambda_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.pdfs}",
            lambda_releases_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.releases}",
            lambda_return404_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.default}",
            authorizer_uri = module.authorize.authorizer_uri,
            authorizer_credentials = module.authorize.authorizer_credentials,
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
#     api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
#     database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
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
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
    timeout             = var.endpoint_timeout
    memory_size         = var.endpoint_memory_size
}


module "authorize" {
    source = "./authorize"

    project             = var.project
    function_name       = local.function_names.authorizer
    task_class          = local.task_classes.authorizer
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
}


module "etl_convert" {
    source = "./etl"

    project             = var.project
    function_name           = local.function_names.convert
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    database_name           = aws_db_instance.cpt_api_database.name
    database_host           = aws_db_instance.cpt_api_database.address
    data_pipeline_ingestion = true
    parent_function         = aws_lambda_function.ingestion_etl_router

    variables               = {
        EXTRACTOR_CLASS             = "datalabs.etl.cpt.ingest.extract.CPTTextDataExtractorTask"
        EXTRACTOR_INCLUDENAMES      = "True"
        EXTRACTOR_BUCKET            = data.aws_ssm_parameter.ingestion_bucket.arn
        EXTRACTOR_BASEPATH          = data.aws_ssm_parameter.s3_base_path.arn
        EXTRACTOR_FILES             = data.aws_ssm_parameter.raw_data_files.arn
        EXTRACTOR_SCHEDULE          = data.aws_ssm_parameter.release_schedule.arn

        TRANSFORMER_CLASS           = "datalabs.etl.parse.transform.ParseToCSVTransformerTask"
        TRANSFORMER_PARSERS         = data.aws_ssm_parameter.raw_data_parsers.arn

        LOADER_CLASS                = "datalabs.etl.s3.load.S3UnicodeTextFileLoaderTask"
        LOADER_BUCKET               = data.aws_ssm_parameter.processed_bucket.arn
        LOADER_FILES                = data.aws_ssm_parameter.converted_data_files.arn
        LOADER_BASEPATH             = data.aws_ssm_parameter.s3_base_path.arn
    }
}


module "etl_bundle_pdf" {
    source = "./etl"

    project             = var.project
    function_name           = local.function_names.bundlepdf
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    database_name           = aws_db_instance.cpt_api_database.name
    database_host           = aws_db_instance.cpt_api_database.address
    data_pipeline_ingestion = true
    parent_function         = aws_lambda_function.ingestion_etl_router

    variables               = {
        EXTRACTOR_CLASS             = "datalabs.etl.s3.extract.S3FileExtractorTask"
        EXTRACTOR_INCLUDENAMES      = "True"
        EXTRACTOR_BUCKET            = data.aws_ssm_parameter.ingestion_bucket.arn
        EXTRACTOR_BASEPATH          = data.aws_ssm_parameter.s3_base_path.arn
        EXTRACTOR_FILES             = data.aws_ssm_parameter.pdf_files.arn

        TRANSFORMER_CLASS           = "datalabs.etl.archive.transform.ZipTransformerTask"

        LOADER_CLASS                = "datalabs.etl.s3.load.S3FileLoaderTask"
        LOADER_BUCKET               = data.aws_ssm_parameter.processed_bucket.arn
        LOADER_BASEPATH             = data.aws_ssm_parameter.s3_base_path.arn
        LOADER_FILES                = "pdfs.zip"
    }
}


module "etl_load" {
    source = "./etl"

    project             = var.project
    function_name           = local.function_names.loaddb
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    database_name           = aws_db_instance.cpt_api_database.name
    database_host           = aws_db_instance.cpt_api_database.address
    data_pipeline_api       = true
    parent_function         = aws_lambda_function.processed_etl_router
    timeout                 = 300

    variables               = {
        EXTRACTOR_CLASS             = "datalabs.etl.s3.extract.S3UnicodeTextFileExtractorTask"
        EXTRACTOR_INCLUDENAMES      = "True"
        EXTRACTOR_BUCKET            = data.aws_ssm_parameter.processed_bucket.arn
        EXTRACTOR_BASEPATH          = data.aws_ssm_parameter.s3_base_path.arn
        EXTRACTOR_FILES             = data.aws_ssm_parameter.raw_csv_files.arn

        TRANSFORMER_CLASS           = "datalabs.etl.cpt.api.transform.CSVToRelationalTablesTransformerTask"
        TRANSFORMER_DATABASE_NAME        = aws_db_instance.cpt_api_database.name
        TRANSFORMER_DATABASE_BACKEND     = "postgresql+psycopg2"
        TRANSFORMER_DATABASE_HOST        = aws_db_instance.cpt_api_database.address
        # TRANSFORMER_DATABASE_USERNAME    = data.aws_ssm_parameter.database_username.arn
        # TRANSFORMER_DATABASE_PASSWORD    = data.aws_ssm_parameter.database_password.arn
        TRANSFORMER_DATABASE_SECRET      = data.aws_secretsmanager_secret.database.arn

        LOADER_CLASS                = "datalabs.etl.cpt.api.load.CPTRelationalTableLoaderTask"
        LOADER_DATABASE_NAME        = aws_db_instance.cpt_api_database.name
        LOADER_DATABASE_BACKEND     = "postgresql+psycopg2"
        LOADER_DATABASE_HOST        = aws_db_instance.cpt_api_database.address
        # LOADER_DATABASE_USERNAME    = data.aws_ssm_parameter.database_username.arn
        # LOADER_DATABASE_PASSWORD    = data.aws_ssm_parameter.database_password.arn
        LOADER_DATABASE_SECRET      = data.aws_secretsmanager_secret.database.arn
    }
}


locals {
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
        BudgetCode          = "PBW"
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
        modifier                    = "${var.project}GetModifier"
        modifiers                   = "${var.project}GetModifiers"
        pla_details                 = "${var.project}GetPLADetails"
        all_pla_details             = "${var.project}GetAllPLADetails"
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
