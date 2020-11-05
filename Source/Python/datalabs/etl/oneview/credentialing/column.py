"""Oneview Credentialing Table Columns"""

customer_columns = {
    'CUSTOMER_KEY': 'id',
    'CUSTOMER_NBR': 'number',
    'CUSTOMER_ISELL_LOGIN': 'isell_login',
    'CUSTOMER_NAME': 'name',
    'CUSTOMER_TYPE': 'type',
    'CUSTOMER_TYPE_DESC': 'type_description',
    'CUSTOMER_CATEGORY': 'category',
    'CUSTOMER_CATEGORY_DESC': 'category_description',
    'Street 1ST': 'street_one',
    'Street 2ND': 'street_two',
    'Street 3RD': 'street_three',
    'City': 'city',
    'State': 'state',
    'Zipcode': 'zipcode',
    'Phone Number': 'phone_number'
}

product_columns = {
    'PRODUCT_ID': 'id',
    'PRODUCT_DESC': 'description'
}

order_columns = {
    'FACT_EPROFILE_KEY': 'id',
    'CUSTOMER_KEY': 'customer',
    'ORDER_PRODUCT_ID': 'product',
    'ORDER_NBR': 'number',
    'ORDER_PHYSICIAN_HIST_KEY': 'medical_education_number',
    'FULL_DT': 'date'
}
