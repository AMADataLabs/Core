""" Table column definitions - will be removed / reworked """
STANDARD_RESULTS_COLUMNS = [
    'sample_id',
    'row_id',
    'physician_me_number',
    'physician_first_name',
    'physician_middle_name',
    'physician_last_name',
    'suffix',
    'degree',
    'office_address_line_1',
    'office_address_line_2',
    'office_address_city',
    'office_address_state',
    'office_address_zip',
    'office_address_verified_updated',
    'office_telephone',
    'office_phone_verified_updated',
    'office_fax',
    'office_fax_verified_updated',
    'specialty',
    'specialty_updated',
    'present_employment_code',
    'present_employment_updated',
    'comments',
    'source',
    'source_date'
]

VALIDATION_RESULTS_COLUMNS = [
    'sample_id',
    'row_id',
    'study_cd',
    'me_no',
    'fname',
    'mname',
    'lname',
    'suffix',
    'degree',
    'lable_name',
    'office_phone',
    'polo_addr_line_0',
    'polo_addr_line_1',
    'polo_addr_line_2',
    'polo_city',
    'polo_state',
    'polo_zip',
    'polo_zipext',
    'original_phone',
    'correct_phone',
    'reason_phone_incorrect',
    'reason_phone_other',
    'captured_number',
    'correct_address',
    'reason_addr_incorrect',
    'reason_addr_other',
    'no_longer_at_addr_comment',
    'captured_add0',
    'captured_add1',
    'captured_add2',
    'captured_city',
    'captured_state',
    'captured_zip',
    'captured_zipext',
    'lastcall',
    'adcid',
    'secondattempt',
    'result_of_call'
]

SAMPLE_COLUMNS = [
    'sample_id',
    'row_id',
    'survey_month',
    'survey_year',
    'survey_type',
    'sample_source',
    'me',
    'entity_id',
    'first_name',
    'middle_name',
    'last_name',
    'suffix',
    'polo_comm_id',
    'polo_mailing_line_1',
    'polo_mailing_line_2',
    'polo_city',
    'polo_state',
    'polo_zip',
    'phone_comm_id',
    'telephone_number',
    'prim_spec_cd',
    'description',
    'pe_cd',
    'fax_number'
]

# column names of Excel files sent/received to/from Humach
STANDARD_RESULTS_COLUMNS_EXPECTED = [
    'SAMPLE_ID',
    'ROW_ID',
    'PHYSICIAN ME NUMBER',
    'PHYSICIAN FIRST NAME',
    'PHYSICIAN MIDDLE NAME',
    'PHYSICIAN LAST NAME',
    'SUFFIX',
    'DEGREE',
    'OFFICE ADDRESS LINE 1',
    'OFFICE ADDRESS LINE 2',
    'OFFICE ADDRESS CITY',
    'OFFICE ADDRESS STATE',
    'OFFICE ADDRESS ZIP',
    'OFFICE ADDRESS VERIFIED/UPDATED',
    'OFFICE TELEPHONE',
    'OFFICE PHONE VERIFIED/UPDATED',
    'OFFICE FAX',
    'OFFICE FAX VERIFIED/UPDATED',
    'SPECIALTY',
    'SPECIALTY UPDATED',
    'PRESENT EMPLOYMENT CODE',
    'PRESENT EMPLOYMENT UPDATED',
    'COMMENTS',
    'SOURCE',
    'SOURCE DATE'

]

VALIDATION_RESULTS_COLUMNS_EXPECTED = [
    'SAMPLE_ID',
    'ROW_ID',
    'STUDY_CD',
    'ME_NO',
    'FNAME',
    'MNAME',
    'LNAME',
    'SUFFIX',
    'DEGREE',
    'LABLE_NAME',
    'OFFICE_PHONE',
    'POLO_ADDR_LINE_0',
    'POLO_ADDR_LINE_1',
    'POLO_ADDR_LINE_2',
    'POLO_CITY',
    'POLO_STATE',
    'POLO_ZIP',
    'POLO_ZIPEXT',
    'ORIGINAL_PHONE',
    'CORRECT_PHONE',
    'REASON_PHONE_INCORRECT',
    'REASON_PHONE_OTHER',
    'CAPTURED_NUMBER',
    'CORRECT_ADDRESS',
    'REASON_ADDR_INCORRECT',
    'REASON_ADDR_OTHER',
    'NO_LONGER_AT_ADDR_COMMENT',
    'CAPTURED_ADD0',
    'CAPTURED_ADD1',
    'CAPTURED_ADD2',
    'CAPTURED_CITY',
    'CAPTURED_STATE',
    'CAPTURED_ZIP',
    'CAPTURED_ZIPEXT',
    'LASTCALL',
    'ADCID',
    'SECONDATTEMPT',
    'RESULT_OF_CALL'
]

SAMPLE_COLUMNS_EXPECTED = [
    'SAMPLE_ID',
    'ROW_ID',
    'SURVEY_MONTH',
    'SURVEY_YEAR',
    'SURVEY_TYPE',
    'SAMPLE_SOURCE',
    'ME',
    'ENTITY_ID',
    'FIRST_NAME',
    'MIDDLE_NAME',
    'LAST_NAME',
    'SUFFIX',
    'POLO_COMM_ID',
    'POLO_MAILING_LINE_1',
    'POLO_MAILING_LINE_2',
    'POLO_CITY',
    'POLO_STATE',
    'POLO_ZIP',
    'PHONE_COMM_ID',
    'TELEPHONE_NUMBER',
    'PRIM_SPEC_CD',
    'DESCRIPTION',
    'PE_CD',
    'FAX_NUMBER'
]

reference_table_columns = [
    'humach_sample_id',
    'other_sample_id',
    'other_sample_source'
]
