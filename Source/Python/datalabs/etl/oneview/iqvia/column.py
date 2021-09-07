"""Oneview Physician Table Columns"""

BUSINESS_COLUMNS = {
    'IMS_ORG_ID': 'id',
    'BUSINESS_NAME': 'name',
    'DBA_NAME': 'doing_business_as',
    'ADDRESS_ID': 'iqvia_address_id',
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
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude',
    'OWNER_STATUS': 'owner_status',
    'PROFIT_STATUS': 'profit_status',
    'PRIMARY_COT_ID': 'primary_class_of_trade',
    'COT_CLASSIFICATION_ID': 'class_of_trade_classification',
    'COT_FACILITY_TYPE_ID': 'class_of_trade_facility_type',
    'COT_FACILITY_TYPE': 'class_of_trade_facility_type_description',
    'COT_SPECIALTY_ID': 'class_of_trade_specialty',
    'COT_SPECIALTY':'class_of_trade_specialty_description',
    'RECORD_TYPE': 'record_type',
    'TTL_LICENSE_BEDS': 'total_licensed_beds',
    'TTL_CENSUS_BEDS': 'total_census_beds',
    'TTL_STAFFED_BEDS': 'total_staffed_beds',
    'TEACHING_HOSP': 'teaching_hospital',
    'COMMHOSP': 'hospital_care',
    'MSA': 'metropolitan_statistical_area',
    'FIPS_STATE': 'federal_information_processing_standard_state',
    'FIPS_COUNTY': 'federal_information_processing_standard_county',
    'NUM_OF_PROVIDERS': 'number_of_providers',
    'ELECTRONIC_MED_REC': 'electronic_medical_record',
    'EPRESCRIBE': 'electronically_prescribe',
    'PAYPERFORM': 'pay_for_performance',
    'DEACTIVATION_REASON': 'deactivation_reason',
    'REFERBACK_IMS_ORG_ID': 'replacement_business',
    'STATUS_INDICATOR': 'status_indicator',
    'BATCH_BUSINESS_DATE': 'batch_business_date'
}

PROVIDER_COLUMNS = {
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
    'PRIMARY_PROF_CODE': 'primary_profession',
    'PRIMARY_PROF_DESC': 'primary_profession_description',
    'UPIN': 'unique_physician_identification_number ',
    'NPI': 'national_provider_identifier',
    'STATUS_DESC': 'status_description',
    'BATCH_BUSINESS_DATE': 'batch_business_date'
}

PROVIDER_AFFILIATION_COLUMNS = {
    'id': 'id',
    'IMS_ORG_ID': 'business',
    'ME': 'medical_education_number',
    'AFFIL_TYPE_ID': 'type',
    'AFFIL_TYPE_DESC': 'description',
    'AFFIL_IND': 'primary',
    'AFFIL_RANK': 'rank',
    'AFFIL_GROUP_CODE': 'group',
    'AFFIL_GROUP_DESC': 'group_description',
    'BATCH_BUSINESS_DATE': 'batch_business_date'
}

CORPORATE_PARENT_BUSINESS = {
    'CORP_PARENT_IMS_ORG_ID': 'child',
    'CORP_PARENT_NAME': 'parent'
}

SUBSIDIARY_BUSINESS = {
    'OWNER_SUB_IMS_ORG_ID': 'subsidiary',
    'OWNER_SUB_NAME': 'owner'
}

IQVIA_DATE = {
    'BATCH_BUSINESS_DATE': 'date'
}
