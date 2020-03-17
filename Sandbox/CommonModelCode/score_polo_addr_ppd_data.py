# Kari Palmier    8/16/19    Created
#
#############################################################################
import logging
import os
import sys
import warnings

import pandas as pd

from   datalabs.analysis.exception import InvalidDataException

warnings.filterwarnings("ignore")

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# Get path of general (common) code and add it to the python path variable

# curr_path = os.path.abspath(__file__)
# print(curr_path)
# slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
# base_path = curr_path[:slash_ndx[-2] + 1]
# gen_path = base_path + 'CommonModelCode\\'
# # gen_path = 'C:\\Data-Science\\Code-Library\\Common_Model_Code\\'
# sys.path.insert(0, gen_path)

from process_model_data import convert_data_types, create_new_addr_vars, clean_model_data, convert_int_to_cat
from class_model_creation import get_class_predictions


def fill_nan_model_vars(data_df):
    data_cols = data_df.columns.values
    for name in data_cols:

        if all(data_df[name].isna()):
            data_df[name] = 0

    return data_df


def score_polo_addr_data(ppd_scoring_df, model, model_vars, init_model_vars, info_vars):
    print('SCORE_POLO_ADDR_DATA')
    assert len(ppd_scoring_df) > 0
    print(ppd_scoring_df.dtypes)
    print('#'*80)
    # Convert data types to expected
    assert 'ent_comm_begin_dt' in ppd_scoring_df.columns.values
    MISSING_VARIABLES = [
        'lic_state_match_0', 'ent_comm_src_cat_code_ADMIT-HOS', 'ent_comm_src_cat_code_ECF-CNVRSN',
        'ent_comm_src_cat_code_GROUP', 'ent_comm_src_cat_code_PHNSURV', 'ent_comm_src_cat_code_SCHL-HOSP',
        'ent_comm_comm_type_GROUP', 'ppd_pe_cd_11', 'ppd_pe_cd_110',
    ]

    ppd_scoring_converted_df = convert_data_types(ppd_scoring_df)
    missing_variables = [var for var in MISSING_VARIABLES if var not in ppd_scoring_converted_df.columns.values]
    LOGGER.debug('PPD Scoring Converted missing variables: %s', missing_variables)

    # Create new model variables
    ppd_scoring_new_df = create_new_addr_vars(ppd_scoring_converted_df)
    LOGGER.debug('PPD Scoring New has all variables? %s', any(var in ppd_scoring_new_df.columns.values for var in MISSING_VARIABLES))
    # LOGGER.debug('PPD Scoring New Column Names: %s', ppd_scoring_new_df.columns.values)

    # Get data wtih just model variables
    model_df = ppd_scoring_new_df.loc[:, init_model_vars]
    LOGGER.debug('Model has all variables? %s', any(var in model_df.columns.values for var in MISSING_VARIABLES))
    # LOGGER.debug('Model Column Names: %s', model_df.columns.values)

    # Deal with any NaN or invalid entries
    model_clean_df, ppd_scoring_clean_df = clean_model_data(model_df, ppd_scoring_new_df)
    LOGGER.debug('Model Clean has all variables? %s', any(var in model_clean_df.columns.values for var in MISSING_VARIABLES))
    # LOGGER.debug('Model Clean Column Names: %s', model_clean_df.columns.values)

    # Convert int variables to integer from float
    model_convert_df = convert_int_to_cat(model_clean_df)
    LOGGER.debug('Model Convert has all variables? %s', any(var in model_convert_df.columns.values for var in MISSING_VARIABLES))

    # Convert categorical variables to dummy variables
    model_data_all = pd.get_dummies(model_convert_df)
    LOGGER.debug('Model Data All has all variables? %s', any(var in model_data_all.columns.values for var in MISSING_VARIABLES))

    # Keep only variable required for the model
    model_vars = list(model_vars)
    LOGGER.debug('Model Variables: %s', model_vars)
    LOGGER.debug('Model Data Column Names: %s', list(model_data_all.columns.values))

    missing_variables = [var for var in model_vars if var not in model_data_all.columns.values]
    if missing_variables:
        raise InvalidDataException(f'Model input data is missing the following columns: {missing_variables}')

    model_data_pruned = model_data_all.loc[:, model_vars]
    model_data_pruned = fill_nan_model_vars(model_data_pruned)

    # outpath = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Polo_Rank_Model\\Data\\2020-01-30_Model_Data.csv'
    # print('Writing processed data to {}'.format(outpath))
    # model_data_pruned.to_csv(outpath, index=False)
    # get model class probabilites and predictions
    preds, probs = get_class_predictions(model, model_data_pruned, 0.5, False)

    model_pred_df = model_df[:]
    model_pred_df[info_vars] = ppd_scoring_df.loc[:, info_vars]
    model_pred_df['pred_class'] = preds
    model_pred_df['pred_probability'] = probs

    return model_pred_df, model_data_pruned


def score_polo_ppd_data(ppd_scoring_df, model, model_vars):
    print('SCORE_POLO_PPD_DATA')
    assert len(ppd_scoring_df) > 0
    init_model_vars = ['lic_state_match', 'pcp', 'ent_comm_src_cat_code', 'ent_comm_comm_type',
                       'addr_age_yrs', 'yop_yrs', 'doctor_age_yrs', 'ppd_address_type', 'ppd_region',
                       'ppd_division', 'ppd_group', 'ppd_msa_population_size', 'ppd_md_do_code',
                       'ppd_micro_metro_ind', 'ppd_gender', 'ppd_top_cd', 'ppd_pe_cd', 'ppd_prim_spec_cd',
                       'ppd_polo_state',
                       'hist_ent_id_addr_count', 'hist_ent_all_addr_count', 'curr_ent_id_addr_count',
                       'curr_ent_all_addr_count', 'curr_usg_all_addr_count']

    # note these are in the order desired for the sample output
    info_vars = ['ppd_me', 'ppd_first_name', 'ppd_middle_name', 'ppd_last_name', 'ppd_suffix',
                 'ppd_polo_mailing_line_1', 'ppd_polo_mailing_line_2', 'ppd_polo_city',
                 'ppd_polo_state', 'ppd_polo_zip',
                 'ppd_telephone_number', 'ppd_prim_spec_cd', 'ppd_pe_cd', 'ppd_fax_number',
                 'post_addr_line1', 'post_addr_line2', 'post_city_cd', 'post_state_cd',
                 'post_zip', 'ent_comm_comm_type', 'ent_comm_begin_dt', 'ent_comm_end_dt',
                 'ent_comm_comm_id', 'ent_comm_entity_id']
    assert 'ent_comm_begin_dt' in ppd_scoring_df
    model_pred_df, model_data_pruned = score_polo_addr_data(ppd_scoring_df, model,
                                                            model_vars, init_model_vars, info_vars)

    return model_pred_df, model_data_pruned


def score_polo_wslive_data(wslive_scoring_df, model, model_vars):
    init_model_vars = ['lic_state_match', 'pcp', 'ent_comm_src_cat_code', 'ent_comm_comm_type',
                       'addr_age_yrs', 'yop_yrs', 'doctor_age_yrs', 'ppd_address_type', 'ppd_region',
                       'ppd_division', 'ppd_group', 'ppd_msa_population_size', 'ppd_md_do_code',
                       'ppd_micro_metro_ind', 'ppd_gender', 'ppd_top_cd', 'ppd_pe_cd', 'ppd_prim_spec_cd',
                       'ppd_polo_state',
                       'hist_ent_id_addr_count', 'hist_ent_all_addr_count', 'curr_ent_id_addr_count',
                       'curr_ent_all_addr_count', 'curr_usg_all_addr_count']

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
                 'ADDR_STATUS', 'post_addr_line1', 'post_addr_line2', 'post_city_cd', 'post_state_cd',
                 'post_zip', 'ent_comm_comm_type', 'ent_comm_begin_dt', 'ent_comm_end_dt',
                 'ent_comm_comm_id', 'ent_comm_entity_id',
                 'WSLIVE_ADDR_KEY', 'INIT_SMPL_ADDR_KEY', 'ent_addr_key']

    model_pred_df, model_data_pruned = score_polo_addr_data(wslive_scoring_df, model,
                                                            model_vars, init_model_vars, info_vars)

    return model_pred_df, model_data_pruned
