# Compatibility with TE state
output "vpc_id" {
  value = [aws_vpc.datalake.id]
}


output "subnet_ids" {
  value = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
}


output "vpc_endpoint_execapi_id" {
    value = aws_vpc_endpoint.apigw.id
}
