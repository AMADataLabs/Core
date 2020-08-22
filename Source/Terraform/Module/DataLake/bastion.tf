resource "aws_key_pair" "bastion_key" {
    key_name   = "DataLakeBastionKey"
    public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC1hAjzoPEq0TgzOms2U0AGSZwsLo64tE41PXD99DlKZIB9dZM4/tkIqvQ0a1k/MrJT+O7qB8T3ad8T6M4nHCfKIThG6rqhkK/DSKw8o8B4ZvejYRulSAzfdamgHdr4RXnP/3qPwu5mz7sWGlvJezbb5tx/rw1nIqvFArB7PFQ23rFwqvZn6FlchKkjGLhIfXwUYH4Sm+COaR/kavIsl6W5sLzWwjF02gRqvTdb4AZljWVGG7meDJUI9yxAUPkI5oKOen4k912iJq5mjbtZ23etV4uahl19K3q8aVgwSnCfaDG+CDoTAkIi+iRMaUIEv4f0eZct77jLH0YdbQ9LLLAf"

    tags = merge(local.tags, {Name = "Data Lake Bastion Key"})
}


resource "aws_security_group" "bastion_ssh" {
  name        = "Bastion SSH"
  description = "Allow SSH inbound traffic to bastions"
  vpc_id      = aws_vpc.datalake.id

  ingress {
    description = "SSH from VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

    tags = merge(local.tags, {Name = "Bastion SG"})
}


resource "aws_subnet" "bastion" {
  vpc_id            = aws_vpc.datalake.id
  cidr_block        = "172.31.100.0/24"
  # availability_zone = "us-west-2a"

    tags = merge(local.tags, {Name = "Data Lake Bastion Subnet"})
}


resource "aws_instance" "bastion" {
    ami                     = data.aws_ami.ubuntu.id
    instance_type           = "t2.micro"
    key_name                = aws_key_pair.bastion_key.key_name
    subnet_id               = aws_subnet.bastion.id
    vpc_security_group_ids  = [aws_security_group.bastion_ssh.id]

    tags = merge(local.tags, {Name = "Data Lake Bastion", OS = "Ubuntu 18.04"})
}


data "aws_ami" "ubuntu" {
    most_recent = true

    filter {
        name   = "name"
        values = ["ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-*"]
        }

    filter {
        name   = "virtualization-type"
        values = ["hvm"]
    }

    owners = ["099720109477"] # Canonical
}
