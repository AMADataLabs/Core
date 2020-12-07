"""Oneview Credentialing Table Columns"""

CUSTOMER_COLUMNS = {
    'CUSTOMER_KEY': 'id',
    'CUSTOMER_NBR': 'number',
    'CUSTOMER_ISELL_LOGIN': 'isell_username',
    'CUSTOMER_NAME': 'name',
    'CUSTOMER_TYPE': 'type',
    'CUSTOMER_TYPE_DESC': 'type_description',
    'CUSTOMER_CATEGORY': 'category',
    'CUSTOMER_CATEGORY_DESC': 'category_description'
}

PRODUCT_COLUMNS = {
    'PRODUCT_ID': 'id',
    'PRODUCT_DESC': 'description'
}

ORDER_COLUMNS = {
    'FACT_EPROFILE_KEY': 'id',
    'CUSTOMER_KEY': 'customer',
    'ORDER_PRODUCT_ID': 'product',
    'ORDER_NBR': 'number',
    'MED_EDU_NBR': 'medical_education_number',
    'FULL_DT': 'date'
}

CUSTOMER_ADDRESSES_COLUMNS = {
    'id': 'id',
    'number': 'number',
    'isell_username': 'isell_username',
    'name': 'name',
    'type': 'type',
    'type_description': 'type_description',
    'category': 'category',
    'category_description': 'category_description',
    'street_one': 'address_1',
    'street_two': 'address_2',
    'street_three': 'address_3',
    'city': 'city',
    'state': 'state',
    'zipcode': 'zipcode',
    'phone_number': 'phone_number',
    'company_name': 'company_name'
}