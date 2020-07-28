resource "aws_ssm_parameter" "database_username" {
    name  = "/DataLabs/CPT/RDS/username"
    type  = "String"
    value = "DataLabs_UI"
    tags = local.tags
}


resource "aws_ssm_parameter" "database_password" {
    name    = "/DataLabs/CPT/RDS/password"
    type    = "SecureString"
    key_id  = aws_kms_key.cpt.key_id
    value   = var.password
    tags    = local.tags
}


resource "aws_ssm_parameter" "s3_base_path" {
    name  = "/DataLabs/CPT/s3/base_path"
    type  = "String"
    value = "AMA/CPT"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_data_files" {
    name  = "/DataLabs/CPT/data/raw_files"
    type  = "String"
    value = "standard/SHORTU.txt,standard/MEDU.txt,standard/LONGULT.txt,standard/MODUL.txt,standard/Consumer Friendly Descriptors/ConsumerDescriptor.txt,standard/Clinician Descriptors/ClinicianDescriptor.txt,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA,CPT Link/history/Deleted_DTK_tab.txt,CPT Link/history/HistoryModifiers_DTK_tab.txt,CPT Link/history/History_DTK_tab.txt"
    tags = local.tags
}


resource "aws_ssm_parameter" "release_schedule" {
    name  = "/DataLabs/CPT/release/schedule"
    type  = "String"
    value = "{\"ANNUAL\": [\"1-Sep\", \"1-Jan\"], \"Q1\": [\"1-Jan\", \"1-Apr\"], \"Q2\": [\"1-Apr\", \"1-Jul\"], \"Q3\": [\"1-Jul\", \"1-Oct\"], \"Q4\": [\"1-Oct\", \"1-Jan\"]}"
    tags = local.tags
}


resource "aws_ssm_parameter" "raw_data_parsers" {
    name  = "/DataLabs/CPT/data/parsers"
    type  = "String"
    value = "datalabs.curate.parse.CSVParser,datalabs.curate.cpt.descriptor.ShortDescriptorParser,datalabs.curate.cpt.descriptor.MediumDescriptorParser,datalabs.curate.cpt.descriptor.LongDescriptorParser,datalabs.curate.cpt.modifier.ModifierParser,datalabs.curate.cpt.descriptor.ConsumerDescriptorParser,datalabs.curate.cpt.descriptor.ClinicianDescriptorParser,datalabs.curate.cpt.pla.PLAParser,datalabs.curate.cpt.link.history.DeletionHistoryParser,datalabs.curate.cpt.link.history.ModifierHistoryParser,datalabs.curate.cpt.link.history.CodeHistoryParser"
    tags = local.tags
}


resource "aws_ssm_parameter" "converted_data_files" {
    name  = "/DataLabs/CPT/data/converted_files"
    type  = "String"
    value = "standard/release.csv,standard/SHORTU.csv,standard/MEDU.csv,standard/LONGULT.csv,standard/MODUL.csv,standard/Consumer Friendly Descriptors/ConsumerDescriptor.csv,standard/Clinician Descriptors/ClinicianDescriptor.csv,standard/Proprietary Laboratory Analyses (PLA) Codes/CPTPLA.csv,CPT Link/history/Deleted_DTK_tab.csv,CPT Link/history/HistoryModifiers_DTK_tab.csv,CPT Link/history/History_DTK_tab.csv"
    tags = local.tags
}


resource "aws_ssm_parameter" "pdf_files" {
    name  = "/DataLabs/CPT/data/pdf_files"
    type  = "String"
    value = "CPT Link Release Notes *.pdf,standard/AnesthesiaGuidelines.pdf,standard/AppendixB.pdf,standard/AppendixN.pdf,standard/AppendixO.pdf,standard/CategoryIIGuidelines.pdf,standard/CategoryIIIGuidelines.pdf,standard/CPT * README.pdf,standard/EvalManagementGuidelines.pdf,standard/MedicineGuidelines.pdf,standard/PathLabGuidelines.pdf,standard/RadiologyGuidelines.pdf,standard/Clinician Descriptors/* Clinician Descriptors README.pdf,standard/Consumer Friendly Descriptors/* Consumer Friendly Descriptors README.pdf"
    tags = local.tags
}
