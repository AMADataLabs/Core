provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}


resource "aws_kms_key" "cpt" {
  description   = "${local.project} KMS key"
  tags          = merge(local.tags, {Name = "${local.project} parameter encryption key"})
}


resource "aws_kms_alias" "cpt" {
  name          = "alias/DataLabs/${local.project}"
  target_key_id = aws_kms_key.cpt.key_id
}


resource "aws_ssm_parameter" "s3_base_path" {
    name  = "/DataLabs/${local.project}/s3/base_path"
    type  = "String"
    value = "AMA/CPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_data_files" {
    name  = "/DataLabs/${local.project}/data/raw_files"
    type  = "String"
    value = "ETL_TRIGGER,standard/SHORTU.txt,standard/MEDU.txt,standard/LONGULT.txt,standard/MODUL.txt,standard/Consumer Friendly Descriptors/ConsumerDescriptor.txt,standard/Clinician Descriptors/ClinicianDescriptor.txt,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA,CPT Link/history/Deleted_DTK_tab.txt,CPT Link/history/HistoryModifiers_DTK_tab.txt,CPT Link/history/History_DTK_tab.txt"
    tags = local.tags
}


resource "aws_ssm_parameter" "release_schedule" {
    name  = "/DataLabs/${local.project}/release/schedule"
    type  = "String"
    value = "{\"ANNUAL\": [\"1-Sep\", \"1-Jan\"], \"Q1\": [\"1-Jan\", \"1-Apr\"], \"Q2\": [\"1-Apr\", \"1-Jul\"], \"Q3\": [\"1-Jul\", \"1-Oct\"], \"Q4\": [\"1-Oct\", \"1-Jan\"]}"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_data_parsers" {
    name  = "/DataLabs/${local.project}/data/parsers"
    type  = "String"
    value = "datalabs.curate.parse.CSVParser,datalabs.curate.parse.PassThroughParser,datalabs.curate.cpt.descriptor.ShortDescriptorParser,datalabs.curate.cpt.descriptor.MediumDescriptorParser,datalabs.curate.cpt.descriptor.LongDescriptorParser,datalabs.curate.cpt.modifier.ModifierParser,datalabs.curate.cpt.descriptor.ConsumerDescriptorParser,datalabs.curate.cpt.descriptor.ClinicianDescriptorParser,datalabs.curate.cpt.pla.PLAParser,datalabs.curate.cpt.link.history.DeletionHistoryParser,datalabs.curate.cpt.link.history.ModifierHistoryParser,datalabs.curate.cpt.link.history.CodeHistoryParser"
    tags = local.tags
}


resource "aws_ssm_parameter" "converted_data_files" {
    name  = "/DataLabs/${local.project}/data/converted_files"
    type  = "String"
    value = "standard/release.csv,ETL_TRIGGER,standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Consumer Friendly Descriptors/ConsumerDescriptor.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv,CPT Link/history/Deleted_DTK_tab.csv,CPT Link/history/HistoryModifiers_DTK_tab.csv,CPT Link/history/History_DTK_tab.csv"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_csv_files" {
    name  = "/DataLabs/${local.project}/data/raw_csv_files"
    type  = "String"
    value = "standard/release.csv,standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Consumer Friendly Descriptors/ConsumerDescriptor.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv,CPT Link/history/Deleted_DTK_tab.csv,CPT Link/history/HistoryModifiers_DTK_tab.csv,CPT Link/history/History_DTK_tab.csv"
    tags = local.tags
}


resource "aws_ssm_parameter" "pdf_files" {
    name  = "/DataLabs/${local.project}/data/pdf_files"
    type  = "String"
    value = "CPT Link Release Notes *.pdf,standard/AnesthesiaGuidelines.pdf,standard/AppendixB.pdf,standard/AppendixN.pdf,standard/AppendixO.pdf,standard/CategoryIIGuidelines.pdf,standard/CategoryIIIGuidelines.pdf,standard/CPT * README.pdf,standard/EvalManagementGuidelines.pdf,standard/MedicineGuidelines.pdf,standard/PathLabGuidelines.pdf,standard/RadiologyGuidelines.pdf,standard/Clinician Descriptors/* Clinician Descriptors README.pdf,standard/Consumer Friendly Descriptors/* Consumer Friendly Descriptors README.pdf,standard/SurgeryGuidelines.pdf"
    tags = local.tags
}


resource "aws_ssm_parameter" "passport_url" {
    name  = "/DataLabs/${local.project}/auth/passport_url"
    type  = "String"
    value = "https://amapassport-staging.ama-assn.org/auth/entitlements/list/CPTAPI"
    # value = "https://amapassport-test.ama-assn.org/auth/entitlements/list/CPTAPI"
    tags = local.tags
}


resource "aws_secretsmanager_secret" "database" {
    name        = "DataLabs/CPT/API/database"
    description = "CPT API database credentials"
    kms_key_id  = aws_kms_key.cpt.arn

    tags = merge(local.tags, {Name = "Data Labs ${local.project} Database Secret"})
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id     = aws_secretsmanager_secret.database.id
  secret_string = jsonencode(
    {
        username = "datalabs"
        password = var.database_password
        engine = "postgres"
        port = 5432
        dbname = "cpt"
        dbinstanceIdentifier = "cpt"
    }
  )
}

locals {
    system_tier         = "Application"
    na                  = "N/A"
    budget_code         = "PBW"
    owner               = "DataLabs"
    project             = "CPT"
    tags                = {
        Name                = "Data Labs ${local.project} Parameter"
        Env                 = data.aws_ssm_parameter.account_environment.value
        Contact             = data.aws_ssm_parameter.contact.value
        SystemTier          = local.system_tier
        DRTier              = local.na
        DataClassification  = local.na
        BudgetCode          = local.budget_code
        Owner               = local.owner
        Group               = local.owner
        Department          = "HSG"
        Project             = local.project
        OS                  = local.na
        EOL                 = local.na
        MaintenanceWindow   = local.na
    }
}
