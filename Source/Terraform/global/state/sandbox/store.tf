provider "aws" {
    region = "us-east-1"
}


module "terraform_state" {
    source = "../../../module/state"

    environment = "Sandbox"
    contact     = "peter.lane@ama-assn.org"
}
