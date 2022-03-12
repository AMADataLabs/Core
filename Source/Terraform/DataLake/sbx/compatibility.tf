# Additional resources that are not part of the TE DataLake stack

module "datalabs_terraform_state" {
  source  = "../../Module/DataLake"
  project = "DataLake"
}


resource "aws_ecr_repository" "datanow" {
  name = "datanow"

  tags = merge(local.tags, { Name = "Data Labs Data Lake DataNow Container Repository" })
}
