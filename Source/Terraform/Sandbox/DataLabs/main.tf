provider "aws" {
    region = "us-east-1"
}


module "datalabs_terraform_state" {
    source                      = "../../Module/DataLabs"
    project                     = "DataLabs"
    bitbucket_username          = "hsgdatalabs"
    bitbucket_app_password      = var.bitbucket_app_password
}
