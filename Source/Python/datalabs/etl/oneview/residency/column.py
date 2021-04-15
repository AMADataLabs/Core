"""Oneview Residency Table Columns"""

PROGRAM_COLUMNS = {
    'pgm_id': 'id',
    'pgm_name': 'name',
    'pgm_web_address': 'web_address',
    'addr1': 'address_1',
    'addr2': 'address_2',
    'addr3': 'address_3',
    'city': 'city',
    'state': 'state',
    'Zip+4': 'zipcode',
    'ins_id': 'institution',
}

MEMBER_COLUMNS = {
    'pgm_id': 'program',
    'pers_type': 'personnel_type',
    'aamc_id': 'aamc_id',
    'pers_name_first': 'first_name',
    'pers_name_mid': 'middle_name',
    'pers_name_last': 'last',
    'pers_name_sfx': 'suffix',
    'pers_deg1': 'degree_1',
    'pers_deg2': 'degree_2',
    'pers_deg3': 'degree_3',
}

INSTITUTION_COLUMNS = {
    'inst_id': 'id',
    'ins_name': 'name',
    'affiliation_type': 'affiliation',
    'pri_clinical_loc_ind': 'primary_clinical_location'
}
