### replicate AMA Terraform Enterprise stacks ###

output "vpc_id" {
  value = [aws_vpc.foundations.id]
}


output "subnet_ids" {
  value = [aws_subnet.foundations_private1.id, aws_subnet.foundations_private2.id]
}


output "vpc_endpoint_execapi_id" {
    value = aws_vpc_endpoint.apigw.id
}


### extra output that may be useful, but shouldn't be used in TE-destined app stacks ##

output "public_subnet_ids" {
  value =   value = [aws_subnet.foundations_public1.id, aws_subnet.foundations_public2.id]
}
