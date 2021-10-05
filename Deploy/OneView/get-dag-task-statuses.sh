#!/bin/bash

EXECUTION_TIME=$1  # 2021-09-29 22:45:00

TASKS=(
    # "EXTRACT_PPD"
    # "EXTRACT_PHYSICIAN_RACE_ETHNICITY"
    # "EXTRACT_MEDICAL_STUDENT"
    # "SUPPLEMENT_PPD_TABLE"
    # "SPLIT_PPD_TABLE"

    # "EXTRACT_PARTY_KEYS_1"
    # "EXTRACT_PARTY_KEYS_2"
    # "EXTRACT_PARTY_KEYS_3"
    # "CONCATENATE_PARTY_KEYS"
    # "CREATE_PHYSICIAN_NPI_TABLE"
    # "EXTRACT_MEMBERSHIP_DATA"
    # "CREATE_PHYSICIAN_TABLE_1"
    # "CREATE_PHYSICIAN_TABLE_2"
    # "CREATE_PHYSICIAN_TABLE_3"
    # "CREATE_PHYSICIAN_TABLE_4"
    # "CREATE_PHYSICIAN_TABLE_5"
    # "CREATE_PHYSICIAN_TABLE_6"
    # "CONCATENATE_PHYSICIAN_TABLE"
    #
    # "EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY"
    # "CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE"
    # "LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE"
    #
    # "EXTRACT_SPECIALTY"
    # "CREATE_SPECIALTY_TABLE"
    # "REMOVE_UNUSED_SPECIALTIES"
    # "LOAD_SPECIALTY_TABLE"
    #
    # "EXTRACT_CORE_BASED_STATISTICAL_AREA"
    # "CREATE_CORE_BASED_STATISTICAL_AREA_TABLE"
    # "LOAD_CORE_BASED_STATISTICAL_AREA_TABLE"
    #
    # "EXTRACT_TYPE_OF_PRACTICE"
    # "CREATE_TYPE_OF_PRACTICE_TABLE"
    # "LOAD_TYPE_OF_PRACTICE_TABLE"
    #
    # "EXTRACT_PRESENT_EMPLOYMENT"
    # "CREATE_PRESENT_EMPLOYMENT_TABLE"
    # "LOAD_PRESENT_EMPLOYMENT_TABLE"
    #
    # "EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY"
    # "CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE"
    # "LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE"
    #
    # "EXTRACT_STATE_TABLE"
    # "CREATE_STATE_TABLE"
    # "LOAD_STATE_TABLE"
    #
    # "LOAD_PHYSICIAN_TABLE_1"
    # "LOAD_PHYSICIAN_TABLE_2"
    # "LOAD_PHYSICIAN_TABLE_3"
    # "LOAD_PHYSICIAN_TABLE_4"
    # "LOAD_PHYSICIAN_TABLE_5"
    # "LOAD_PHYSICIAN_TABLE_6"

    # "EXTRACT_RESIDENCY"
    # "CREATE_RESIDENCY_TABLES"
    # "LOAD_RESIDENCY_INSTITUTION_TABLE"
    # "LOAD_RESIDENCY_PROGRAM_TABLE"
    # "LOAD_RESIDENCY_PERSONNEL_TABLE"
    "CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE"

    "EXTRACT_MELISSA"
    "CREATE_MELISSA_TABLES"
    "LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE"
    "LOAD_COUNTY_TABLE"
    "LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE"
    "LOAD_ZIP_CODE_TABLE"
    "LOAD_AREA_CODE_TABLE"
    "LOAD_CENSUS_TABLE"
    "LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE"

    "EXTRACT_IQVIA_BUSINESS"
    "EXTRACT_IQVIA_PROVIDER"
    "EXTRACT_IQVIA_PROVIDER_AFFILIATION"
    "CREATE_IQVIA_UPDATE_TABLE"
    "CREATE_BUSINESS_AND_PROVIDER_TABLES"
    "LOAD_IQVIA_BUSINESS_PROVIDER_TABLES"
    "LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE"
    "LOAD_IQVIA_UPDATE_TABLE"

    "EXTRACT_CREDENTIALING"
    "EXTRACT_CREDENTIALING_ADDRESSES"
    "CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES"
    "CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE"
    "MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE"
    "CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE"
    "LOAD_CREDENTIALING_CUSTOMER_PRODUCT_TABLES"
    "LOAD_CREDENTIALING_ORDER_TABLE"
    "LOAD_LINKING_TABLES"

    "EXTRACT_HISTORICAL_RESIDENT"
    "CREATE_HISTORICAL_RESIDENT_TABLE"
    "LOAD_HISTORICAL_RESIDENT_TABLE"
    "EXTRACT_MEDICAL_STUDENT"

    "EXTRACT_STATE_TABLE"
    "EXTRACT_CLASS_OF_TRADE_TABLE"
    "CREATE_STATIC_REFERENCE_TABLE"
    "CREATE_STATE_TABLE"
    "CREATE_CLASS_OF_TRADE_TABLE"
    "LOAD_CLASS_OF_TRADE_TABLE"
    "LOAD_STATE_TABLE"
    "LOAD_STATIC_REFERENCE_TABLE"
    "EXTRACT_MEDICAL_SCHOOL_TABLE"
    "CREATE_MEDICAL_SCHOOL_TABLE"
    "LOAD_MEDICAL_SCHOOL_TABLE"

)

ENVIRONMENT_FILE=$(apigw_assume_role.sh dev | grep source | awk '{print $2}')
source ${ENVIRONMENT_FILE}

for task in ${TASKS[@]}; do
    echo $task: $(aws dynamodb get-item \
        --table-name DataLake-dag-state-dev \
        --key '{"name": {"S": "ONEVIEW__'${task}'"}, "execution_time": {"S": "'"${EXECUTION_TIME}"'"}}' \
        | grep -A 1 status | grep '"S"' | awk '{print $2}'
    )
done
