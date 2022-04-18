# resource "aws_key_pair" "bastion_key" {
#     key_name   = "DataLakeBastionKey"
#     public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMdCgPAcG2MsIQF7Zds/qaGTMNjWNeYIQXdwb+HvtSqJrtRDXo/XZUu6m4MUrFs0n6vDleSfAafp3xZ9VLLQN/6vVIuJW9GDRiJl1fqPessQxKKFGqJuSv+TrZ20RiUkUpGOmUKcBB6N1Hwkqped2DfTYIX9If3i4OKgdFETg8U2jlxFixvOtruSosm8g/xsHC2Xmnvv4VTc1DwWECARVYGRFUIdIdy/PNkIhzWGNp1aDs5ALzpZ5WhtqkzSBr49tYbALORs/DcN5CV6RSZ3vaVvcXoQrweDl6Cd5eCTiPxU8xsZGZFFPwWK9VXXrLJkpSMeqZmHacPNRAp+zd2zOZ"
#
#     tags = merge(local.tags, {Name = "Data Lake Bastion Key"})
# }
#
#
# resource "aws_security_group" "bastion_ssh" {
#   name        = "Bastion SSH"
#   description = "Allow SSH inbound traffic to bastions"
#   vpc_id      = aws_vpc.datalake.id
#
#     ingress {
#         description = "SSH"
#         from_port   = 22
#         to_port     = 22
#         protocol    = "tcp"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     ingress {
#       description = "SNMP"
#       from_port   = 161
#       to_port     = 161
#       protocol    = "udp"
#       cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     egress {
#         from_port   = 0
#         to_port     = 0
#         protocol    = "-1"
#         cidr_blocks = ["0.0.0.0/0"]
#     }
#
#     tags = merge(local.tags, {Name = "Bastion SG"})
# }
#
#
# resource "aws_subnet" "bastion" {
#   vpc_id            = aws_vpc.datalake.id
#   cidr_block        = "172.31.100.0/24"
#   # availability_zone = "us-west-2a"
#
#     tags = merge(local.tags, {Name = "Data Lake Bastion Subnet"})
# }
#
#
# resource "aws_route_table_association" "bastion" {
#     subnet_id      = aws_subnet.bastion.id
#     route_table_id = aws_vpc.datalake.default_route_table_id
# }
#
#
# resource "aws_instance" "bastion" {
#     ami                             = data.aws_ami.ubuntu.id
#     instance_type                   = "t2.micro"
#     key_name                        = aws_key_pair.bastion_key.key_name
#     subnet_id                       = aws_subnet.bastion.id
#     vpc_security_group_ids          = [aws_security_group.bastion_ssh.id]
#     associate_public_ip_address     = true
#
#     tags = merge(local.tags, {Name = "Data Lake Bastion", OS = "Ubuntu 18.04"})
# }
#
#
# data "aws_ami" "ubuntu" {
#     most_recent = true
#
#     filter {
#         name   = "name"
#         values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20200821.1"]
#         }
#
#     filter {
#         name   = "virtualization-type"
#         values = ["hvm"]
#     }
#
#     owners = ["099720109477"] # Canonical
# }
