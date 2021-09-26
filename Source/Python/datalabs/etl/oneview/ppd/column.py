"""Oneview Physician Table Columns"""

PPD_COLUMNS = {
    'meNumber': 'meNumber'
    'addressType': 'addressType'
    'MailingName': 'MailingName'
    'lastName': 'lastName'
    'firstName': 'firstName'
    'middleName': 'middleName'
    'suffixCode': 'suffixCode'
    'preferredLine_addr_1': 'preferredLine_addr_1'
    'preferredLine_addr_2': 'preferredLine_addr_2'
    'preferredCity': 'preferredCity'
    'preferredStateCode': 'preferredStateCode'
    'preferredZipCode': 'preferredZipCode'
    'prefferedSectorZipPlus4': 'prefferedSectorZipPlus4'
    'preferredCarrierRoute': 'preferredCarrierRoute'
    'undeliverableFlag': 'undeliverableFlag'
    'fips_county': 'fips_county'
    'fips_state': 'fips_state'
    'printerControlCodeBegin': 'printerControlCodeBegin'
    'barCodeZip': 'barCodeZip'
    'barCodePlus4': 'barCodePlus4'
    'deliveryPointCode': 'deliveryPointCode'
    'checkDigit': 'checkDigit'
    'printerControlCodeEnd': 'printerControlCodeEnd'
    'region': 'region'
    'division': 'division'
    'group': 'group'
    'tract': 'tract'
    'suffix': 'suffix'
    'blockGroup': 'blockGroup'
    'MSA_Poulation': 'MSA_Poulation'
    'Micro_Metro_ind': 'Micro_Metro_ind'
    'CBSA': 'CBSA'
    'CBSA_devision': 'CBSA_devision'
    'degree_type': 'degree_type'
    'birthYear': 'birthYear'
    'birthCity': 'birthCity'
    'birthState': 'birthState'
    'birthCountry': 'birthCountry'
    'gender': 'gender'
    'preferredPhoneNumber': 'preferredPhoneNumber'
    'pendingDeadIndicator': 'pendingDeadIndicator'
    'faxNumber': 'faxNumber'
    'topCode': 'topCode'
    'PECode': 'PECode'
    'primSpecialty': 'primSpecialty'
    'secondarySpecialty': 'secondarySpecialty'
    'MPACode': 'MPACode'
    'PRAAwardRecepient': 'PRAAwardRecepient'
    'PRAAwardExpirationDate': 'PRAAwardExpirationDate'
    'GMEConfirmationFlag': 'GMEConfirmationFlag'
    'fromDate': 'fromDate'
    'endDate': 'endDate'
    'yearInProgram': 'yearInProgram'
    'postGradYear': 'postGradYear'
    'gmePrimarySpecialtyCode': 'gmePrimarySpecialtyCode'
    'gmeSecondarySpecialtyCode': 'gmeSecondarySpecialtyCode'
    'TrainingType': 'TrainingType'
    'GMEHospitalState': 'GMEHospitalState'
    'GMEHospitalID': 'GMEHospitalID'
    'gradSchoolState': 'gradSchoolState'
    'gradSchoolCd': 'gradSchoolCd'
    'gradYear': 'gradYear'
    'contactIndicator': 'contactIndicator'
    'noWebInfoRls': 'noWebInfoRls'
    'CBSA_DIVISION': 'CBSA_DIVISION'
    'DEGREE_TYPE': 'DEGREE_TYPE'
    'BIRTH_YEAR': 'BIRTH_YEAR'
    'BIRTH_CITY': 'BIRTH_CITY'
    'BIRTH_STATE': 'BIRTH_STATE'
    'BIRTH_COUNTRY': 'BIRTH_COUNTRY'
    'GENDER': 'GENDER'
    'PREFERREDPHONENUMBER': 'PREFERREDPHONENUMBER'
    'PENDINGDEAD_IND': 'PENDINGDEAD_IND'
    'FAXNUMBER': 'FAXNUMBER'
    'TOPCODE': 'TOPCODE'
    'PECODE': 'PECODE'
    'PRIMSPECIALTY': 'PRIMSPECIALTY'
    'SECONDARYSPECIALTY': 'SECONDARYSPECIALTY'
    'MPACODE': 'MPACODE'
    'PRAAWARDRECIPIENT': 'PRAAWARDRECIPIENT'
    'PRAEXPIRATIONDATE': 'PRAEXPIRATIONDATE'
    'GMECONFIRMFLAG': 'GMECONFIRMFLAG'
    'FROMDATE': 'FROMDATE'
    'ENDDATE': 'ENDDATE'
    'YEARINPROGRAM': 'YEARINPROGRAM'
    'POSTGRADYEAR': 'POSTGRADYEAR'
    'GMEPRIMSPECIALTY': 'GMEPRIMSPECIALTY'
    'GMESECSPECIALTY': 'GMESECSPECIALTY'
    'TRAINING_TYPE': 'TRAINING_TYPE'
    'GMEHOSPITALSTATE': 'GMEHOSPITALSTATE'
    'GMEHOSPITALID': 'GMEHOSPITALID'
    'GRADSCHOOLSTATE': 'GRADSCHOOLSTATE'
    'GRADSCHOOLCODE': 'GRADSCHOOLCODE'
    'GRADYEAR': 'GRADYEAR'
    'NOCONTACT_IND': 'NOCONTACT_IND'
    'NOWEBIND': 'NOWEBIND'
    'PDRP_FLAG': 'PDRP_FLAG'
    'PDRP_DATE': 'PDRP_DATE'
    'POLO_ADDR2': 'POLO_ADDR2'
    'POLO_ADDR1': 'POLO_ADDR1'
    'POLO_CITY': 'POLO_CITY'
    'POLO_STATE': 'POLO_STATE'
    'POLO_ZIP': 'POLO_ZIP'
    'POLO_PLUS4': 'POLO_PLUS4'
    'POLOCARRIERROUTE': 'POLOCARRIERROUTE'
    'MOSTRECENTFORMERLASTNAME': 'MOSTRECENTFORMERLASTNAME'
    'MOSTRECENTFORMERMIDDLENAME': 'MOSTRECENTFORMERMIDDLENAME'
    'MOSTRECENTFORMERFIRSTNAME': 'MOSTRECENTFORMERFIRSTNAME'
    'NEXTMOSTRECENTFORMERLASTNAME': 'NEXTMOSTRECENTFORMERLASTNAME'
    'NEXTMOSTRECENTFORMERMIDDLENAME': 'NEXTMOSTRECENTFORMERMIDDLENAME'
    'NEXTMOSTRECENTFORMERFIRSTNAME': 'NEXTMOSTRECENTFORMERFIRSTNAME'
    'PDRP_date': 'PDRP_date'
    'poloLine_addr_2': 'poloLine_addr_2'
    'poloLine_addr_1': 'poloLine_addr_1'
    'cityName': 'cityName'
    'poloState': 'poloState'
    'poloZipCode': 'poloZipCode'
    'poloSector': 'poloSector'
    'poloCarrierRoute': 'poloCarrierRoute'
    'mostRecentFormerLastName': 'mostRecentFormerLastName'
    'mostRecentFormerMiddleName': 'mostRecentFormerMiddleName'
    'mostRecentFormerFirstName': 'mostRecentFormerFirstName'
    'nextMostRecentFormerLastName': 'nextMostRecentFormerLastName'
    'nextMostRecentFormerMiddleName': 'nextMostRecentFormerMiddleName'
    'nextMostRecentFormerFirstName': 'nextMostRecentFormerFirstName'
    'PARTY_ID': 'PARTY_ID'
    'entity_id': 'entity_id'
    'npi': 'npi'
    'race_ethnicity': 'race_ethnicity'
}

MEDICAL_STUDENT_COLUMNS = {
    'me_no': 'meNumber',
    'mailing_name': 'MailingName',
    'last_name': 'lastName',
    'first_name': 'firstName',
    'middle_name': 'middleName',
    'suffix': 'suffixCode',
    'mail_line_1': 'preferredLine_addr_1',
    'mail_line_2': 'preferredLine_addr_2',
    'state': 'preferredStateCode',
    'zipcode': 'preferredZipCode',
    'sector': 'prefferedSectorZipPlus4',
    'addr_city': 'preferredCity',
    'carrier_route': 'preferredCarrierRoute',
    'addr_undeliver_flg': 'undeliverableFlag',
    'fips_county': 'fips_county',
    'fips_state': 'fips_state',
    'region': 'region',
    'msa_population_size': 'MSA_Poulation',
    'division': 'division',
    'group': 'group',
    'tract': 'tract',
    'census_suffix': 'suffix',
    'block_group': 'blockGroup',
    'metro_micro_indicator': 'metro_micro_indicator',
    'CBSA': 'CBSA',
    'cbsa_division_indicator': 'CBSA_devision',
    'school_name': 'GRADSCHOOLCODE',
    'school_state': 'GRADSCHOOLSTATE',
    'grad_year': 'GRADYEAR',
    'birth_year': 'BIRTH_YEAR',
    'birth_city': 'BIRTH_CITY',
    'birth_state': 'BIRTH_STATE',
    'birth_country': 'BIRTH_COUNTRY',
    'gender': 'GENDER',
    'addr_type_ind': 'addressType',
    'phone_no': 'PREFERREDPHONENUMBER',
    'presumed_dead': 'PENDINGDEAD_IND',
    'contact_flg': 'NOCONTACT_IND'
}

NPI_COLUMNS = {
    'PARTY_ID': 'PARTY_ID',
    'meNumber': 'meNumber',
    'npi': 'npi',
    'entity_id': 'entity_id'
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
    'region': 'region',
    'division': 'division',
    'group': 'group',
    'tract': 'tract',
    'suffix': 'suffix',
    'blockGroup': 'block_group',
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
    'CBSA_DIVISION': 'core_based_statistical_area_division',
    'DEGREE_TYPE': 'degree_type',
    'BIRTH_YEAR': 'birth_year',
    'BIRTH_CITY': 'birth_city',
    'BIRTH_STATE': 'birth_state',
    'BIRTH_COUNTRY': 'birth_country',
    'GENDER': 'gender',
    'PREFERREDPHONENUMBER': 'telephone_number',
    'PENDINGDEAD_IND': 'presumed_dead',
    'FAXNUMBER': 'fax_number',
    'TOPCODE': 'type_of_practice',
    'PECODE': 'present_employment',
    'PRIMSPECIALTY': 'primary_specialty',
    'SECONDARYSPECIALTY': 'secondary_specialty',
    'MPACODE': 'major_professional_activity',
    'PRAAWARDRECIPIENT': 'physician_recognition_award_recipient',
    'PRAEXPIRATIONDATE': 'physician_recognition_award_expiration_date',
    'GMECONFIRMFLAG': 'graduate_medical_education_confirm',
    'FROMDATE': 'from_date',
    'ENDDATE': 'end_date',
    'YEARINPROGRAM': 'year_in_program',
    'POSTGRADYEAR': 'post_graduate_year',
    'GMEPRIMSPECIALTY': 'graduate_medical_education_primary_specialty',
    'GMESECSPECIALTY': 'graduate_medical_education_secondary_specialty',
    'TRAINING_TYPE': 'training_type',
    'GMEHOSPITALSTATE': 'graduate_medical_education_hospital_state',
    'GMEHOSPITALID': 'graduate_medical_education_hospital',
    'GRADSCHOOLSTATE': 'medical_school_state',
    'GRADSCHOOLCODE': 'medical_school',
    'GRADYEAR': 'medical_school_graduation_year',
    'NOCONTACT_IND': 'no_contact_type',
    'NOWEBIND': 'no_web',
    'PDRP_FLAG': 'physician_data_restriction_program',
    'PDRP_DATE': 'physician_data_restriction_program_date',
    'POLO_ADDR2': 'polo_address_2',
    'POLO_ADDR1': 'polo_address_1',
    'POLO_CITY': 'polo_city',
    'POLO_STATE': 'polo_state',
    'POLO_ZIP': 'polo_zipcode',
    'POLO_PLUS4': 'polo_sector',
    'POLOCARRIERROUTE': 'polo_carrier_route',
    'MOSTRECENTFORMERLASTNAME': 'most_recent_former_last_name',
    'MOSTRECENTFORMERMIDDLENAME': 'most_recent_former_middle_name',
    'MOSTRECENTFORMERFIRSTNAME': 'most_recent_former_first_name',
    'NEXTMOSTRECENTFORMERLASTNAME': 'next_most_recent_former_last_name',
    'NEXTMOSTRECENTFORMERMIDDLENAME': 'next_most_recent_former_middle_name',
    'NEXTMOSTRECENTFORMERFIRSTNAME': 'next_most_recent_former_first_name',
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
    'PARTY_ID': 'party_id',
    'entity_id': 'entity_id',
    'npi': 'national_provider_identifier',
    'race_ethnicity': 'race_ethnicity'
}
