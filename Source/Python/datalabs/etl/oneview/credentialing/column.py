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
