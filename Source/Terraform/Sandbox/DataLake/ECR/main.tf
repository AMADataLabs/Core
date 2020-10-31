provider "aws" {
    region = "us-east-1"
    version = "~> 3.0"
}

resource "aws_ecr_repository" "datanow" {
  name                 = "datanow"
}
