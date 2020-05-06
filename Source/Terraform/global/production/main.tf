provider "aws" {
    region = "us-east-1"
}


module "terraform_state" {
    source = "../state"

    environment         = "Production"
    contact             = "peter.lane@ama-assn.org"
    state_bucket        = "ama-hsg-datalabs-datalake-terraform-state"
}
