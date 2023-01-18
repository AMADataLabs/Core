"""Oneview Physician Table Columns"""

PPD_COLUMNS = {
    'meNumber': 'meNumber',
    'recordIndicator': 'recordIndicator',
    'updateType': 'updateType',
    'addressType': 'addressType',
    'MailingName': 'MailingName',
    'lastName': 'lastName',
    'firstName': 'firstName',
    'middleName': 'middleName',
    'suffixCode': 'suffixCode',
    'preferredLine_addr_2': 'preferredLine_addr_2',
    'preferredLine_addr_1': 'preferredLine_addr_1',
    'preferredCity': 'preferredCity',
    'preferredStateCode': 'preferredStateCode',
    'preferredZipCode': 'preferredZipCode',
    'prefferedSectorZipPlus4': 'prefferedSectorZipPlus4',
    'preferredCarrierRoute': 'preferredCarrierRoute',
    'undeliverableFlag': 'undeliverableFlag',
    'fips_county': 'fips_county',
    'fips_state': 'fips_state',
    'printerControlCodeBegin': 'printerControlCodeBegin',
    'barCodeZip': 'barCodeZip',
    'barCodePlus4': 'barCodePlus4',
    'deliveryPointCode': 'deliveryPointCode',
    'checkDigit': 'checkDigit',
    'printerControlCodeEnd': 'printerControlCodeEnd',
    'region': 'region',
    'division': 'division',
    'group': 'group',
    'tract': 'tract',
    'suffix': 'suffix',
    'blockGroup': 'blockGroup',
    'MSA_Poulation': 'MSA_Poulation',
    'Micro_Metro_ind': 'Micro_Metro_ind',
    'CBSA': 'CBSA',
    'CBSA_devision': 'CBSA_devision',
    'degree_type': 'degree_type',
    'birthYear': 'birthYear',
    'birthCity': 'birthCity',
    'birthState': 'birthState',
    'birthCountry': 'birthCountry',
    'gender': 'gender',
    'preferredPhoneNumber': 'preferredPhoneNumber',
    'pendingDeadIndicator': 'pendingDeadIndicator',
    'faxNumber': 'faxNumber',
    'topCode': 'topCode',
    'PECode': 'PECode',
    'primSpecialty': 'primSpecialty',
    'secondarySpecialty': 'secondarySpecialty',
    'MPACode': 'MPACode',
    'PRAAwardRecepient': 'PRAAwardRecepient',
    'PRAAwardExpirationDate': 'PRAAwardExpirationDate',
    'GMEConfirmationFlag': 'GMEConfirmationFlag',
    'fromDate': 'fromDate',
    'endDate': 'endDate',
    'yearInProgram': 'yearInProgram',
    'postGradYear': 'postGradYear',
    'gmePrimarySpecialtyCode': 'gmePrimarySpecialtyCode',
    'gmeSecondarySpecialtyCode': 'gmeSecondarySpecialtyCode',
    'TrainingType': 'TrainingType',
    'GMEHospitalState': 'GMEHospitalState',
    'GMEHospitalID': 'GMEHospitalID',
    'gradSchoolState': 'gradSchoolState',
    'gradSchoolCd': 'gradSchoolCd',
    'gradYear': 'gradYear',
    'contactIndicator': 'contactIndicator',
    'noWebInfoRls': 'noWebInfoRls',
    'noPrescribeIndicator': 'noPrescribeIndicator',
    'PDRP_flag': 'PDRP_flag',
    'PDRP_date': 'PDRP_date',
    'poloLine_addr_2': 'poloLine_addr_2',
    'poloLine_addr_1': 'poloLine_addr_1',
    'cityName': 'cityName',
    'poloState': 'poloState',
    'poloZipCode': 'poloZipCode',
    'poloSector': 'poloSector',
    'poloCarrierRoute': 'poloCarrierRoute',
    'mostRecentFormerLastName': 'mostRecentFormerLastName',
    'mostRecentFormerMiddleName': 'mostRecentFormerMiddleName',
    'mostRecentFormerFirstName': 'mostRecentFormerFirstName',
    'nextMostRecentFormerLastName': 'nextMostRecentFormerLastName',
    'nextMostRecentFormerMiddleName': 'nextMostRecentFormerMiddleName',
    'nextMostRecentFormerFirstName': 'nextMostRecentFormerFirstName',
    'no_release_ind': 'no_release_ind',
    'race_ethnicity': 'race_ethnicity',
    'person_type': 'person_type'
}


NPI_COLUMNS = {
    'PARTY_ID': 'PARTY_ID',
    'meNumber': 'meNumber',
    'npi': 'npi',
    'entity_id': 'entity_id'
}


MEDICAL_STUDENT_COLUMNS = {
    'me_no': 'meNumber',
    'mailing_name': 'MailingName',
    'last_name': 'lastName',
    'first_name': 'firstName',
    'middle_name': 'middleName',
    'suffix': 'suffixCode',
    'mail_line_1': 'preferredLine_addr_2',
    'mail_line_2': 'preferredLine_addr_1',
    'state': 'preferredStateCode',
    'zipcode': 'preferredZipCode',
    'sector': 'prefferedSectorZipPlus4',
    'addr_city': 'preferredCity',
    'carrier_route': 'preferredCarrierRoute',
    'addr_undeliver_flg': 'undeliverableFlag',
    'fips_county': 'fips_county',
    'fips_state': 'fips_state',
    'msa_population_size': 'MSA_Poulation',
    'region': 'region',
    'division': 'division',
    'group': 'group',
    'tract': 'tract',
    'census_suffix': 'suffix',
    'blockGroup': 'blockGroup',
    'metro_micro_indicator': 'Micro_Metro_ind',
    'cbsa': 'CBSA',
    'cbsa_division_indicator': 'CBSA_devision',
    'grad_school_cd': 'gradSchoolCd',
    'school_state': 'gradSchoolState',
    'grad_year': 'gradYear',
    'birth_year': 'birthYear',
    'birth_city': 'birthCity',
    'birth_state': 'birthState',
    'birth_country': 'birthCountry',
    'gender': 'gender',
    'addr_type_ind': 'addressType',
    'phone_no': 'preferredPhoneNumber',
    'presumed_dead': 'pendingDeadIndicator',
    'contact_flg': 'contactIndicator',
    'no_release_ind': 'no_release_ind'
}


PHYSICIAN_COLUMNS = {
    'meNumber': 'medical_education_number',
    'addressType': 'address_type',
    'MailingName': 'mailing_name',
    'lastName': 'last_name',
    'firstName': 'first_name',
    'middleName': 'middle_name',
    'suffixCode': 'name_suffix',
    'preferredLine_addr_1': 'preferred_address_1',
    'preferredLine_addr_2': 'preferred_address_2',
    'preferredCity': 'city',
    'preferredStateCode': 'state',
    'preferredZipCode': 'zipcode',
    'prefferedSectorZipPlus4': 'sector',
    'preferredCarrierRoute': 'carrier_route',
    'undeliverableFlag': 'address_undeliverable',
    'fips_county': 'federal_information_processing_standard_county',
    'fips_state': 'federal_information_processing_standard_state',
    'printerControlCodeBegin': 'printer_control_code_begin',
    'barCodeZip': 'barcode_zipcode',
    'barCodePlus4': 'barcode_zipcode_plus_4',
    'deliveryPointCode': 'delivery_point',
    'checkDigit': 'check_digit',
    'printerControlCodeEnd': 'printer_control_code_end',
    'region': 'census_region',
    'division': 'census_division',
    'group': 'census_group',
    'tract': 'census_tract',
    'suffix': 'census_suffix',
    'blockGroup': 'census_block_group',
    'MSA_Poulation': 'metropolitan_statistical_area_population',
    'Micro_Metro_ind': 'micro_metro_indicator',
    'CBSA': 'core_based_statistical_area',
    'CBSA_devision': 'core_based_statistical_area_division',
    'degree_type': 'degree_type',
    'birthYear': 'birth_year',
    'birthCity': 'birth_city',
    'birthState': 'birth_state',
    'birthCountry': 'birth_country',
    'gender': 'gender',
    'preferredPhoneNumber': 'telephone_number',
    'pendingDeadIndicator': 'presumed_dead',
    'faxNumber': 'fax_number',
    'topCode': 'type_of_practice',
    'PECode': 'present_employment',
    'primSpecialty': 'primary_specialty',
    'secondarySpecialty': 'secondary_specialty',
    'MPACode': 'major_professional_activity',
    'PRAAwardRecepient': 'physician_recognition_award_recipient',
    'PRAAwardExpirationDate': 'physician_recognition_award_expiration_date',
    'GMEConfirmationFlag': 'graduate_medical_education_confirm',
    'fromDate': 'from_date',
    'endDate': 'end_date',
    'yearInProgram': 'year_in_program',
    'postGradYear': 'post_graduate_year',
    'gmePrimarySpecialtyCode': 'graduate_medical_education_primary_specialty',
    'gmeSecondarySpecialtyCode': 'graduate_medical_education_secondary_specialty',
    'TrainingType': 'training_type',
    'GMEHospitalState': 'graduate_medical_education_hospital_state',
    'GMEHospitalID': 'graduate_medical_education_hospital',
    'gradSchoolState': 'medical_school_state',
    'gradSchoolCd': 'medical_school',
    'gradYear': 'medical_school_graduation_year',
    'contactIndicator': 'no_contact_type',
    'noWebInfoRls': 'no_web',
    'PDRP_flag': 'physician_data_restriction_program',
    'PDRP_date': 'physician_data_restriction_program_date',
    'poloLine_addr_2': 'polo_address_2',
    'poloLine_addr_1': 'polo_address_1',
    'cityName': 'polo_city',
    'poloState': 'polo_state',
    'poloZipCode': 'polo_zipcode',
    'poloSector': 'polo_sector',
    'poloCarrierRoute': 'polo_carrier_route',
    'mostRecentFormerLastName': 'most_recent_former_last_name',
    'mostRecentFormerMiddleName': 'most_recent_former_middle_name',
    'mostRecentFormerFirstName': 'most_recent_former_first_name',
    'nextMostRecentFormerLastName': 'next_most_recent_former_last_name',
    'nextMostRecentFormerMiddleName': 'next_most_recent_former_middle_name',
    'nextMostRecentFormerFirstName': 'next_most_recent_former_first_name',
    'race_ethnicity': 'race_ethnicity',
    'PARTY_ID': 'party_id',
    'entity_id': 'entity_id',
    'npi': 'national_provider_identifier',
    'person_type': 'type',
    'MEMBERSHIP_STATUS': 'membership_status',
    'has_email': 'has_email',
    'no_release_ind': 'no_release'
}