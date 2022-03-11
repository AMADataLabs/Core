# Compatibility with TE state
output "vpc_id" {
  value = data.terraform_remote_state.infrastructure.outputs.vpc_id
}


output "subnet_ids" {
  value = data.terraform_remote_state.infrastructure.outputs.subnet_ids
}


output "vpc_endpoint_execapi_id" {
    value = data.terraform_remote_state.infrastructure.outputs.vpc_endpoint_execapi_id
}
