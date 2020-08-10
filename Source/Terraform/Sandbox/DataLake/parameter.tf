resource "aws_ssm_parameter" "ingestion_bucket" {
    name  = "/DataLabs/${local.project}/ingestion_bucket"
    type  = "String"
    value = format("ama-hsg-datalabs-%s-ingestion-sandbox", lower(local.project))
    tags = local.tags
}


resource "aws_ssm_parameter" "processed_bucket" {
    name  = "/DataLabs/${local.project}/processed_bucket"
    type  = "String"
    value = format("ama-hsg-datalabs-%s-processed-sandbox", lower(local.project))
    tags = local.tags
}
