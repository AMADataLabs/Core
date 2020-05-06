terraform {
    backend "s3" {
        bucket          = "ama-hsg-datalabs-datalake-terraform-state"
        key             = "global/state.tfstate"
        region          = "us-east-1"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }
}
