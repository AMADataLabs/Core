terraform {
    backend "s3" {
        bucket          = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
        key             = "CPTStress/sandbox.tfstate"
        region          = "us-east-1"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }
}
