resource "aws_kms_key" "cpt" {
  description   = "${var.project} KMS key"
  tags          = merge(local.tags, {Name = "${var.project} API encryption key"})
}


resource "aws_kms_alias" "cpt" {
  name          = "alias/DataLabs/${var.project}"
  target_key_id = aws_kms_key.cpt.key_id
}
