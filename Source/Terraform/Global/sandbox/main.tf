provider "aws" {
    region = "us-east-1"
}


module "terraform_state" {
    source = "../state"
}
