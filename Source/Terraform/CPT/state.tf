terraform {
    backend "s3" {
        # bucket          = "ama-hsg-datalabs-datalake-terraform-state-<account environment>"  (i.e. sandbox or production)
        # key             = "CPT/<deploy environment>.tfstate"  (i.e. dev, test, stage, prod)
        region          = "us-east-1"
        dynamodb_table  = "hsg-datalabs-terraform-locks"
    }
}
