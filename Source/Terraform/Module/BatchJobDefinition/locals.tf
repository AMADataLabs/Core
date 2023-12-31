locals {
  region = "us-east-1"

  tags = merge(
    var.tags,
    map(
      "Environment", upper(var.environment),
      "Contact", upper(var.tag_contact),
      "SystemTier", upper(var.tag_systemtier),
      "DRTier", upper(var.tag_drtier),
      "DataClassification", upper(var.tag_dataclassification),
      "BudgetCode", upper(var.tag_budgetcode),
      "Owner", upper(var.tag_owner),
      "ProjectName", upper(var.project),
      "Notes", upper(var.tag_notes),
      "EOL", upper(var.tag_eol),
      "MaintenanceWindow", upper(var.tag_maintwindow)
    )
  )
}
