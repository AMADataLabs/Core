resource "aws_ssm_parameter" "ingestion_bucket" {
    name  = "/DataLabs/DataLake/ingestion_bucket"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-ingestion-sandbox"
    tags = local.tags
}


resource "aws_ssm_parameter" "processed_bucket" {
    name  = "/DataLabs/DataLake/processed_bucket"
    type  = "String"
    value = "ama-hsg-datalabs-datalake-processed-sandbox"
    tags = local.tags
}
