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


resource "aws_api_gateway_rest_api" "cpt_api_gateway" {
    name = "CPT API"
    description = local.spec_description
    body = templatefile(
        "${path.module}/../../../Build/CPT/api.yaml",
        {
            title = "CPT API",
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
            # lambda_latest_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.latest_pdfs}",
            # lambda_pdfs_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.pdfs}",
            lambda_releases_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.releases}",
            lambda_return404_arn = "arn:aws:lambda:${local.region}:${data.aws_caller_identity.account.account_id}:function:${local.function_names.default}",
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
      aws_iam_role.lambda_role.arn
    )))
  }

  lifecycle {
    create_before_destroy = true
  }
}


module "endpoint_descriptor" {
    source = "./endpoint"

    function_name       = local.function_names.descriptor
    task_class          = local.task_classes.descriptor
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_all_descriptors" {
    source = "./endpoint"

    function_name       = local.function_names.descriptors
    task_class          = local.task_classes.descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_consumer_descriptor" {
    source = "./endpoint"

    function_name       = local.function_names.consumer_descriptor
    task_class          = local.task_classes.consumer_descriptor
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_consumer_descriptors" {
    source = "./endpoint"

    function_name       = local.function_names.consumer_descriptors
    task_class          = local.task_classes.consumer_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_clinician_descriptors" {
    source = "./endpoint"

    function_name       = local.function_names.clinician_descriptors
    task_class          = local.task_classes.clinician_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_all_clinician_descriptors" {
    source = "./endpoint"

    function_name       = local.function_names.all_clinician_descriptors
    task_class          = local.task_classes.all_clinician_descriptors
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_pla_details" {
    source = "./endpoint"

    function_name       = local.function_names.pla_details
    task_class          = local.task_classes.pla_details
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_all_pla_details" {
    source = "./endpoint"

    function_name       = local.function_names.all_pla_details
    task_class          = local.task_classes.all_pla_details
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_modifier" {
    source = "./endpoint"

    function_name       = local.function_names.modifier
    task_class          = local.task_classes.modifier
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_modifiers" {
    source = "./endpoint"

    function_name       = local.function_names.modifiers
    task_class          = local.task_classes.modifiers
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_latest_pdfs" {
    source = "./endpoint"

    function_name       = local.function_names.latest_pdfs
    task_class          = local.task_classes.latest_pdfs
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


# module "endpoint_pdfs" {
#     source = "./endpoint"

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

    function_name       = local.function_names.releases
    task_class          = local.task_classes.releases
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "endpoint_default" {
    source = "./endpoint"

    function_name       = local.function_names.default
    task_class          = local.task_classes.default
    region              = local.region
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    api_gateway_id      = aws_api_gateway_rest_api.cpt_api_gateway.id
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
}


module "etl_convert" {
    source = "./etl"

    function_name           = local.function_names.convert
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    database_name           = aws_db_instance.cpt_api_database.name
    database_host           = aws_db_instance.cpt_api_database.address
    data_pipeline_ingestion = true

    variables           = {
        EXTRACTOR_CLASS             = "datalabs.etl.cpt.ingest.extract.CPTTextDataExtractorTask"
        EXTRACTOR_BUCKET            = data.aws_ssm_parameter.ingestion_bucket.value
        EXTRACTOR_BASE_PATH         = data.aws_ssm_parameter.s3_base_path.value
        EXTRACTOR_FILES             = data.aws_ssm_parameter.raw_data_files.value
        EXTRACTOR_RELEASE_SCHEDULE  = data.aws_ssm_parameter.release_schedule.value

        TRANSFORMER_CLASS           = "datalabs.etl.cpt.ingest.transform.CPTFileToCSVTransformerTask"
        TRANSFORMER_PARSERS         = data.aws_ssm_parameter.raw_data_parsers.value

        LOADER_CLASS                = "datalabs.etl.s3.load.S3WindowsTextLoaderTask"
        LOADER_BUCKET               = data.aws_ssm_parameter.processed_bucket.value
        LOADER_FILES                = data.aws_ssm_parameter.converted_data_files.value
        LOADER_BASE_PATH            = data.aws_ssm_parameter.s3_base_path.value
    }
}


module "etl_bundle_pdf" {
    source = "./etl"

    function_name           = local.function_names.bundlepdf
    account_id              = data.aws_caller_identity.account.account_id
    role                    = aws_iam_role.lambda_role.arn
    database_name           = aws_db_instance.cpt_api_database.name
    database_host           = aws_db_instance.cpt_api_database.address
    data_pipeline_ingestion = true

    variables           = {
        EXTRACTOR_CLASS             = "datalabs.etl.s3.extract.S3FileExtractorTask"
        EXTRACTOR_BUCKET            = data.aws_ssm_parameter.ingestion_bucket.value
        EXTRACTOR_BASE_PATH         = data.aws_ssm_parameter.s3_base_path.value
        EXTRACTOR_FILES             = data.aws_ssm_parameter.pdf_files.value

        TRANSFORMER_CLASS           = "datalabs.etl.archive.transform.ZipTransformerTask"

        LOADER_CLASS                = "datalabs.etl.s3.load.S3FileLoaderTask"
        LOADER_BUCKET               = data.aws_ssm_parameter.processed_bucket.value
        LOADER_BASE_PATH            = data.aws_ssm_parameter.s3_base_path.value
        LOADER_FILES                = "pdfs.zip"
    }
}


module "etl_load" {
    source = "./etl"

    function_name       = local.function_names.loaddb
    account_id          = data.aws_caller_identity.account.account_id
    role                = aws_iam_role.lambda_role.arn
    database_name       = aws_db_instance.cpt_api_database.name
    database_host       = aws_db_instance.cpt_api_database.address
    data_pipeline_api   = true

    variables           = {
        EXTRACTOR_CLASS             = "datalabs.etl.s3.extract.S3WindowsTextExtractorTask"
        EXTRACTOR_BUCKET            = data.aws_ssm_parameter.processed_bucket.value
        EXTRACTOR_BASE_PATH         = data.aws_ssm_parameter.s3_base_path.value
        EXTRACTOR_FILES             = data.aws_ssm_parameter.converted_data_files.value

        TRANSFORMER_CLASS           = "datalabs.etl.cpt.api.transform.CSVToRelationalTablesTransformerTask"

        LOADER_CLASS                = "datalabs.etl.cpt.api.load.CPTRelationalTableLoaderTask"
        LOADER_DATABASE_NAME        = aws_db_instance.cpt_api_database.name
        LOADER_DATABASE_BACKEND     = "postgresql+psycopg2"
        LOADER_DATABASE_HOST        = aws_db_instance.cpt_api_database.address
        LOADER_DATABASE_USERNAME    = data.aws_ssm_parameter.database_username.value
        LOADER_DATABASE_PASSWORD    = data.aws_ssm_parameter.database_password.value
    }
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


data "aws_ssm_parameter" "s3_base_path" {
    name  = "/DataLabs/CPT/s3/base_path"
}


data "aws_ssm_parameter" "raw_data_files" {
    name  = "/DataLabs/CPT/data/raw_files"
}


data "aws_ssm_parameter" "release_schedule" {
    name  = "/DataLabs/CPT/release/schedule"
}


data "aws_ssm_parameter" "raw_data_parsers" {
    name  = "/DataLabs/CPT/data/parsers"
}


data "aws_ssm_parameter" "converted_data_files" {
    name  = "/DataLabs/CPT/data/converted_files"
}


data "aws_ssm_parameter" "pdf_files" {
    name  = "/DataLabs/CPT/data/pdf_files"
}


data "aws_ssm_parameter" "contact" {
    name = "/DataLabs/contact"
}


data "aws_ssm_parameter" "ingestion_bucket" {
    name = "/DataLabs/DataLake/ingestion_bucket"
}


data "aws_ssm_parameter" "processed_bucket" {
    name = "/DataLabs/DataLake/processed_bucket"
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
        default                     = "CPTDefault"
        convert                     = "CPTConvert"
        loaddb                      = "CPTLoad"
        bundlepdf                   = "BundlePDF"
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
    }
}
