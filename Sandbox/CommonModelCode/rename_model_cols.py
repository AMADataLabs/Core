# Kari Palmier   9/20/19    Created
#
#############################################################################

def rename_ppd_columns(ppd_df):
    
    rename_dict = {'ADDRESS_TYPE':'ppd_address_type', 'REGION':'ppd_region', 'DIVISION':'ppd_division', 'GROUP':'ppd_group',
                   'MSA_POPULATION_SIZE':'ppd_msa_population_size', 'MD_DO_CODE':'ppd_md_do_code', 
                   'MICRO_METRO_IND':'ppd_micro_metro_ind', 'GENDER':'ppd_gender', 'TOP_CD':'ppd_top_cd', 'PE_CD':'ppd_pe_cd', 
                   'PRIM_SPEC_CD':'ppd_prim_spec_cd', 'POLO_STATE':'ppd_polo_state', 
                   'ME':'ppd_me', 'FIRST_NAME':'ppd_first_name', 'MIDDLE_NAME':'ppd_middle_name', 
                   'LAST_NAME':'ppd_last_name', 'SUFFIX':'ppd_suffix', 'POLO_MAILING_LINE_1':'ppd_polo_mailing_line_1', 
                   'POLO_MAILING_LINE_2':'ppd_polo_mailing_line_2', 'POLO_CITY':'ppd_polo_city', 'POLO_ZIP':'ppd_polo_zip', 
                   'TELEPHONE_NUMBER':'ppd_telephone_number', 'description':'pe_description', 'FAX_NUMBER':'ppd_fax_number',
                   'MEDSCHOOL_GRAD_YEAR':'ppd_medschool_grad_year', 'BIRTH_YEAR':'ppd_birth_year'}
    
    ppd_renamed_df = ppd_df.rename(columns = rename_dict)
    
    return ppd_renamed_df
