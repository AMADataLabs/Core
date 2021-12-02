
resource "aws_acm_certificate" "cert" {
  domain_name               = "*.cptapi.local"
  certificate_authority_arn = "arn:aws:acm-pca:us-east-1:644454719059:certificate-authority/266baa99-df15-4981-8a20-70634c1a88ce"

  tags = merge(local.tags, {Name = "${var.project}-${local.environment}-private-zone-cert"})
}
