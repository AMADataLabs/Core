# Compatibility with TE state
output "vpc_id" {
  value = [aws_vpc.datalake.id]
}

output "subnet_ids" {
  value = [aws_subnet.datalake_public1.id, aws_subnet.datalake_public2.id]
}
