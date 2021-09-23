# Compatibility with TE state
output "vpc_id" {
  value = [aws_vpc.datalake.id]
}


output "subnet_ids" {
  value = local.subnets
}


output "vpc_endpoint_execapi_id" {
    value = aws_vpc_endpoint.apigw.id
}
