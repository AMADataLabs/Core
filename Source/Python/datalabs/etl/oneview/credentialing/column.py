"""Oneview Credentialing Table Columns"""

PRODUCT_COLUMNS = {
    'PRODUCT_ID': 'id',
    'PRODUCT_DESC': 'description'
}

ORDER_COLUMNS = {
    'FACT_EPROFILE_KEY': 'id',
    'CUSTOMER_KEY': 'customer',
    'ORDER_PRODUCT_ID': 'product',
    'ORDER_NBR': 'number',
    'QUANTITY': 'quantity',
    'UPIN_NBR': 'unique_physician_identification_number',
    'MED_EDU_NBR': 'medical_education_number',
    'FULL_DT': 'date',
    'PERSON_ID': 'person_id'
}

CUSTOMER_ADDRESSES_COLUMNS = {
    'CUSTOMER_KEY': 'id',
    'number': 'number',
    'CUSTOMER_NAME': 'name',
    'CUSTOMER_TYPE': 'type',
    'CUSTOMER_TYPE_DESC': 'type_description',
    'CUSTOMER_CATEGORY': 'category',
    'CUSTOMER_CATEGORY_DESC': 'category_description',
    'CURRENT_IND': 'current_indicator',
    'street_one': 'address_1',
    'street_two': 'address_2',
    'street_three': 'address_3',
    'city': 'city',
    'state': 'state',
    'zipcode': 'zipcode',
    'phone_number': 'phone_number',
    'company_name': 'company_name'
}
