"""OneView Linking Table Columns"""
CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS = {
    'pk': 'id',
    'number': 'customer',
    'institution': 'residency_program_institution',
}
CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS = {
    'pk': 'id',
    'number': 'customer',
    'id': 'business',
}
RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS = {
    'pk': 'id',
    'personnel_member': 'personnel_member',
    'medical_education_number': 'medical_education_number'
}

CORPORATE_PARENT_BUSINESS = {
    'IMS_ORG_ID': 'child',
    'CORP_PARENT_IMS_ORG_ID': 'parent'
}
