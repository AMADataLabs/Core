provider "aws" {
    region = "us-east-1"
}


module "terraform_state" {
    source = "../state"

    environment         = "Sandbox"
    contact             = "DataLabs@ama-assn.org"
    state_bucket        = "ama-hsg-datalabs-datalake-terraform-state-sandbox"
}
