from eralchemy import render_er
from datalabs.model.masterfile.oneview import Base

render_er(
  Base,
  'oneview_db.png',
  include_columns=[
    "id",
    "description",
    "medical_education_number",
    "core_based_statistical_area",
    "type_of_practice",
    "present_employment",
    "primary_specialty",
    "secondary_specialty",
    "major_professional_activity",
    "institution",
    "program",
    "business",
    "provider",
    "customer",
    "product",
    "residency_program_institution",
    "business",
    "personnel_member",
    "medical_education_number"
  ]
)

