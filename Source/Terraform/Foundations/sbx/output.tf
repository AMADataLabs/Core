### replicate AMA Terraform Enterprise stacks ###

output "vpc_id" {
  value = [aws_vpc.datalake.id]
}


output "subnet_ids" {
  value = [aws_subnet.datalake_private1.id, aws_subnet.datalake_private2.id]
}


output "vpc_endpoint_execapi_id" {
    value = aws_vpc_endpoint.apigw.id
}


output "vpc_endpoint_opensearch_id" {
    value = aws_opensearchserverless_vpc_endpoint.opensearch.id
}


### extra output that may be useful, but shouldn't be used in TE-destined app stacks ##

output "public_subnet_ids" {
  value = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
}
