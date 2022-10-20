"""Oneview Medical Licenses Table Columns"""

RAW_MEDICAL_LICENSES_COLUMNS = {
    'PARTY_ID': 'PARTY_ID',
    'LIC_NBR': 'number',
    'LIC_STATE': 'state',
    'ISS_DT': 'issue_date',
    'EXP_DT': 'expiry_date',
    'RNW_DT': 'renew_date',
    'DEGREE_CD': 'degree_type',
    'LIC_STATUS': 'status',
    'LIC_TYPE': 'type'
}

MEDICAL_LICENSES_COLUMNS = {
    'number': 'number',
    'meNumber': 'medical_education_number',
    'state': 'state',
    'issue_date': 'issue_date',
    'expiry_date': 'expiry_date',
    'renew_date': 'renew_date',
    'degree_type': 'degree_type',
    'status': 'status',
    'type': 'type'
}
