0# Kari Palmier    8/16/19    Created
#
#############################################################################
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'CommonModelCode\\'
#gen_path = 'C:\\Data-Science\\Code-Library\\Common_Model_Code\\'
sys.path.insert(0, gen_path)

from process_model_data import convert_data_types, create_new_phone_vars, clean_model_data, convert_int_to_cat
from class_model_creation import get_class_predictions


def fill_nan_model_vars(data_df):
    
    data_cols = data_df.columns.values    
    for name in data_cols:
       
        if all(data_df[name].isna()):
            data_df[name] = 0
    
    return data_df

def score_phone_data(ppd_scoring_df, model, model_vars, init_model_vars, info_vars):
    
    # Convert data types to expected
    ppd_scoring_converted_df = convert_data_types(ppd_scoring_df)
    
    # Create new model variables
    ppd_scoring_new_df = create_new_phone_vars(ppd_scoring_converted_df)
    
    # Get data wtih just model variables
    model_df = ppd_scoring_new_df.loc[:, init_model_vars]
    
    # Deal with any NaN or invalid entries
    model_clean_df, ppd_scoring_clean_df = clean_model_data(model_df, ppd_scoring_new_df)
    
    # Convert int variables to integer from float
    model_convert_df = convert_int_to_cat(model_clean_df)
    
    # Convert categorical variables to dummy variables
    model_data_all = pd.get_dummies(model_convert_df)
    
    # rename address type variable if required (due to initial model build data type issue)
    if 'lic_state_match' in model_vars and 'lic_state_match_1' in list(model_data_all.columns.values):
        temp = {'lic_state_match_1': 'lic_state_match'}
        model_data_all = model_data_all.rename(columns = temp)

    # rename address type variable if required (due to initial model build data type issue)
    if 'ppd_address_type_1.0' in model_vars and 'ppd_address_type_1' in list(model_data_all.columns.values):
        temp = {'ppd_address_type_1': 'ppd_address_type_1.0'}
        model_data_all = model_data_all.rename(columns = temp)
    
    if 'ppd_address_type_2.0' in model_vars and 'ppd_address_type_2' in list(model_data_all.columns.values):
        temp = {'ppd_address_type_2': 'ppd_address_type_2.0'}
        model_data_all = model_data_all.rename(columns = temp)
    
    if 'ppd_address_type_3.0' in model_vars and 'ppd_address_type_3' in list(model_data_all.columns.values):
        temp = {'ppd_address_type_3': 'ppd_address_type_3.0'}
        model_data_all = model_data_all.rename(columns = temp)
        
    # Keep only variable required for the model
    model_vars = list(model_vars)
    model_data_pruned = model_data_all.loc[:, model_vars]
    model_data_pruned = fill_nan_model_vars(model_data_pruned)
    
    # get model class probabilites and predictions
    preds, probs = get_class_predictions(model, model_data_pruned, 0.5, False)
    
    model_pred_df = model_df[:]
    model_pred_df[info_vars] = ppd_scoring_df.loc[:, info_vars]
    model_pred_df['pred_class'] = preds
    model_pred_df['pred_probability'] = probs

    return model_pred_df, model_data_pruned


def score_phone_ppd_data(ppd_scoring_df, model, model_vars):

    init_model_vars = ['lic_state_match', 'dpc', 'res', 'pcp', 'phone_src', 'phone_age', 'yop', 
                       'doctor_age_yrs', 'polo_ind', 'ppd_address_type', 'ppd_region', 'ppd_division', 
                       'ppd_group', 'ppd_msa_population_size', 'ppd_md_do_code', 'ppd_micro_metro_ind', 
                       'ppd_gender', 'phone_age_yrs', 'yop_yrs', 'ppd_top_cd', 'ppd_pe_cd', 
                       'ppd_prim_spec_cd', 'ppd_polo_state', 'ent_comm_src_cat_code', 'ent_comm_comm_type',
                       'hist_ent_id_phn_count', 'hist_ent_all_phn_count', 'curr_ent_id_phn_count', 
                       'curr_ent_all_phn_count', 'curr_usg_all_phn_count', 'area_state_match']
    
    # note these are in the order desired for the sample output
    info_vars = ['ppd_me', 'ppd_first_name', 'ppd_middle_name', 'ppd_last_name', 'ppd_suffix', 
                 'ppd_polo_mailing_line_1', 'ppd_polo_mailing_line_2', 'ppd_polo_city', 
                 'ppd_polo_state', 'ppd_polo_zip', 'ppd_telephone_number', 'ppd_prim_spec_cd', 
                 'ppd_pe_cd', 'ppd_fax_number', 'aims_phone', 'ent_comm_comm_type', 
                 'ent_comm_begin_dt', 'ent_comm_end_dt', 'ent_comm_comm_id', 'ent_comm_entity_id']
    
    model_pred_df, model_data_pruned = score_phone_data(ppd_scoring_df, model, 
                                                            model_vars, init_model_vars, info_vars)

    return model_pred_df, model_data_pruned


def score_phone_wslive_data(wslive_scoring_df, model, model_vars):

    init_model_vars = ['lic_state_match', 'dpc', 'res', 'pcp', 'phone_src', 'phone_age', 'yop', 
                       'doctor_age_yrs', 'polo_ind', 'ppd_address_type', 'ppd_region', 'ppd_division', 
                       'ppd_group', 'ppd_msa_population_size', 'ppd_md_do_code', 'ppd_micro_metro_ind', 
                       'ppd_gender', 'phone_age_yrs', 'yop_yrs', 'ppd_top_cd', 'ppd_pe_cd', 
                       'ppd_prim_spec_cd', 'ppd_polo_state', 'ent_comm_src_cat_code', 'ent_comm_comm_type',
                       'hist_ent_id_phn_count', 'hist_ent_all_phn_count', 'curr_ent_id_phn_count', 
                       'curr_ent_all_phn_count', 'curr_usg_all_phn_count', 'area_state_match']
    
    # note these are in the order desired for the sample output
    info_vars = ['ppd_me', 'ppd_first_name', 'ppd_middle_name', 'ppd_last_name', 'ppd_suffix', 
             'ppd_polo_mailing_line_1', 'ppd_polo_mailing_line_2', 'ppd_polo_city', 
             'ppd_polo_state', 'ppd_polo_zip',
             'ppd_telephone_number', 'ppd_prim_spec_cd', 'ppd_pe_cd', 'ppd_fax_number', 
             'INIT_POLO_MAILING_LINE_1', 'INIT_POLO_MAILING_LINE_2', 'INIT_POLO_CITY', 
             'INIT_POLO_STATE', 'INIT_POLO_ZIP', 'INIT_TELEPHONE_NUMBER', 'INIT_FAX_NUMBER',
             'INIT_SAMPLE_MAX_PERFORM_MONTH', 'INIT_SAMPLE_SENT_MONTH', 'INIT_SAMPLE_DATE', 
             'OFFICE_ADDRESS_LINE_2', 'OFFICE_ADDRESS_LINE_1', 'OFFICE_ADDRESS_CITY', 
             'OFFICE_ADDRESS_STATE', 'OFFICE_ADDRESS_ZIP', 'OFFICE_TELEPHONE', 
             'OFFICE_FAX', 'WS_MONTH', 'COMMENTS', 'WSLIVE_FILE_DT', 'SOURCE', 'PPD_DATE',
             'PHONE_STATUS', 'aims_phone', 'ent_comm_comm_type', 'ent_comm_begin_dt', 
             'ent_comm_end_dt', 'ent_comm_comm_id', 'ent_comm_entity_id']
    
    model_pred_df, model_data_pruned = score_phone_data(wslive_scoring_df, model, 
                                                            model_vars, init_model_vars, info_vars)


    return model_pred_df, model_data_pruned
