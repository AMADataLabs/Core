"""Oneview Residency Table Columns"""

PROGRAM_COLUMNS = {
    'pgm_id': 'id',
    'pgm_spec': 'specialty',
    'pgm_inst_control_type': 'institution_control',
    'pgm_sequence_number': 'sequence_number',
    'pgm_federal_code': 'federal_code',
    'pgm_region_code': 'region_code',
    'prm_acgme_accred_ind': 'acgme_accreditation',
    'pgm_name': 'name',
    'pgm_web_address': 'web_address',
    'pgm_contact_dir_ind': 'contact_director',
    'pgm_accred_status': 'accreditation_status',
    'pgm_accred_eff_dt': 'accreditation_effective_date',
    'pgm_init_accred_dt': 'initial_accreditation_date',
    'pgm_accred_length': 'accreditation_length',
    'pgm_yrs_offered': 'years_offered',
    'pgm_gov_affil_ind': 'government_affiliation',
    'pgm_gme_eq_yr': 'graduate_medical_education_equivalent_years',
    'pgm_prelim_yrs_req': 'preliminary_years_required',
    'pgm_prelim_pos_offered': 'preliminary_positions_offered',
    'pgm_type': 'type',
    'pgm_chg_size': 'change_size',
    'pgm_%@_prim_site': 'percent_at_primary_site',
    'pgm_prim_site': 'primary_site',
    'pgm_core_pgm_id': 'core_program',
    'medical_records': 'medical_records',
    'official_addr_ind': 'official_address',
    'pgm_sf_match': 'uses_sfmatch',
    'pgm_oth_match_ind': 'other_match_indicator',
    'pgm_oth_match': 'other_match',
    'pgm_addit_educ_accred_length': 'additional_education_accreditation_length',
    'last_upd_dt_x': 'last_update_date',
    'last_upd_type_x': 'last_update_type',
    'AOA_Ind': 'american_osteopathic_association_indicator',
    'AOA_Program_ID': 'american_osteopathic_association_indicator_program',
    'Osteopathic_principles': 'osteopathic_principles',
    'addr1': 'address_1',
    'addr2': 'address_2',
    'addr3': 'address_3',
    'city': 'city',
    'state': 'state',
    'Zip+4': 'zipcode',
    'ins_id': 'institution',
}

MEMBER_COLUMNS = {
    'id': 'id',
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
    'pers_ph_num': 'phone_number',
    'pers_e-mail': 'email',
    'last_upd_dt': 'last_update_date'
}

INSTITUTION_COLUMNS = {
    'ins_id': 'id',
    'ins_name': 'name',
    'pri_clinical_loc_ind': 'primary_clinical_location',
    'ins_affiliation_type': 'affiliation',
    'last_upd_dt': 'last_update_date'
}
