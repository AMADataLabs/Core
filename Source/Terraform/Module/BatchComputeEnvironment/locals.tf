locals {
  tags = merge(
    var.tags,
    map(
      "Name", upper(var.tag_name),
      "Environment", upper(var.tag_environment),
      "Contact", upper(var.tag_contact),
      "SystemTier", upper(var.tag_systemtier),
      "DRTier", upper(var.tag_drtier),
      "DataClassification", upper(var.tag_dataclassification),
      "BudgetCode", upper(var.tag_budgetcode),
      "Owner", upper(var.tag_owner),
      "ProjectName", upper(var.tag_projectname),
      "Notes", upper(var.tag_notes),
      "EOL", upper(var.tag_eol),
      "MaintenanceWindow", upper(var.tag_maintwindow)
    )
  )

}
