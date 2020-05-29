data "aws_ssm_parameter" "ETL_CONVERTCPT_LAMBDA_FUNCTION" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_LAMBDA_FUNCTION"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_APP" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_APP"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR_BUCKET" {
    name = "/DataLabs/DataLake/ingestion_bucket"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR_BASE_PATH" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR_BASE_PATH"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_EXTRACTOR_FILES" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_EXTRACTOR_FILES"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_TRANSFORMER" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_TRANSFORMER"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_TRANSFORMER_PARSERS" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_TRANSFORMER_PARSERS"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER_BUCKET" {
    name = "/DataLabs/DataLake/processed_bucket"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER_FILES" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER_FILES"
}


data "aws_ssm_parameter" "ETL_CONVERTCPT_LOADER_BASE_PATH" {
    name = "/DataLabs/CPT/ETL_CONVERTCPT_LOADER_BASE_PATH"
}


data "aws_ssm_parameter" "ETL_LOADCPT_LAMBDA_FUNCTION" {
    name = "/DataLabs/CPT/ETL_LOADCPT_LAMBDA_FUNCTION"
}


data "aws_ssm_parameter" "ETL_LOADCPT_APP" {
    name = "/DataLabs/CPT/ETL_LOADCPT_APP"
}


data "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR" {
    name = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR"
}


data "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR_BUCKET" {
    name = "/DataLabs/DataLake/processed_bucket"
}


data "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR_BASE_PATH" {
    name = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR_BASE_PATH"
}


data "aws_ssm_parameter" "ETL_LOADCPT_EXTRACTOR_FILES" {
    name = "/DataLabs/CPT/ETL_LOADCPT_EXTRACTOR_FILES"
}


data "aws_ssm_parameter" "ETL_LOADCPT_TRANSFORMER" {
    name = "/DataLabs/CPT/ETL_LOADCPT_TRANSFORMER"
}


data "aws_ssm_parameter" "ETL_LOADCPT_LOADER" {
    name = "/DataLabs/CPT/ETL_LOADCPT_LOADER"
}
