"""Oneview Physician Table Columns"""

columns = [
    {
        'IMS_ORG_ID': 'id',
        'BUSINESS_NAME': 'name',
        'DBA_NAME': 'doing_business_as',
        'PHYSICAL_ADDR_1': 'physical_address_1',
        'PHYSICAL_ADDR_2': 'physical_address_2',
        'PHYSICAL_CITY': 'physical_city',
        'PHYSICAL_STATE': 'physical_state',
        'PHYSICAL_ZIP': 'physical_zipcode',
        'POSTAL_ADDR_1': 'postal_address_1',
        'POSTAL_ADDR_2': 'postal_address_2',
        'POSTAL_CITY': 'postal_city',
        'POSTAL_STATE': 'postal_state',
        'POSTAL_ZIP': 'postal_zipcode',
        'PHONE': 'phone',
        'FAX': 'fax',
        'WEBSITE': 'website',
        'OWNER_STATUS': 'owner_status',
        'PROFIT_STATUS': 'profit_status'
    },
    {
        'PROFESSIONAL_ID': 'id',
        'ME': 'medical_education_number',
        'FIRST_NAME': 'first_name',
        'MIDDLE_NAME': 'middle_name',
        'LAST_NAME': 'last_name',
        'GEN_SUFFIX': 'suffix',
        'DESIGNATION': 'designation',
        'GENDER': 'gender',
        'ROLE': 'role',
        'PRIMARY_SPEC': 'primary_specialty',
        'SECONDARY_SPEC': 'secondary_specialty',
        'TERTIARY_SPEC': 'tertiary_specialty',
        'PRIMARY_PROF_CODE': 'primary_professional_code',
        'PRIMARY_PROF_DESC': 'primary_professional_description',
        'STATUS_DESC': 'status_description'
    },
    {
        'AFFIL_TYPE_ID': 'id',
        'IMS_ORG_ID': 'business',
        'PROFESSIONAL_ID': 'provider',
        'AFFIL_TYPE_DESC': 'description',
        'AFFIL_IND': 'primary',
        'AFFIL_RANK': 'rank'
    }
]
