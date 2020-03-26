# Kari Palmier    10/9/19    Created
#
#############################################################################
import datetime
import os
import sys
import warnings

import pandas as pd

import datalabs.curate.wslive as wslive
import datalabs.curate.dataframe as df

warnings.filterwarnings("ignore")


def rename_wslive_init_smpl_cols(wslive_init_df):
    
    init_sample_cols = ['POLO_MAILING_LINE_1', 'POLO_MAILING_LINE_2', 'POLO_CITY',
                        'POLO_STATE', 'POLO_ZIP', 'TELEPHONE_NUMBER', 'FAX_NUMBER',
                        'SAMPLE_MAX_PERFORM_MONTH', 'SAMPLE_SENT_MONTH', 'SAMPLE_DATE']
    new_col_dict = {}
    for var in init_sample_cols:
        new_col_dict[var] = 'INIT_' + var
    wslive_init_df = wslive_init_df.rename(columns = new_col_dict)
    
    return wslive_init_df


def get_wslive_ppd_res_data(wslive_df, ppd_df):
    

    wslive_keep_cols = ['PHYSICIAN_ME_NUMBER', 'OFFICE_TELEPHONE', 'OFFICE_FAX', 'OFFICE_ADDRESS_LINE_2',  
                        'OFFICE_ADDRESS_LINE_1', 'OFFICE_ADDRESS_CITY', 'OFFICE_ADDRESS_STATE',  
                        'OFFICE_ADDRESS_ZIP', 'WSLIVE_FILE_DT', 'WS_MONTH', 'COMMENTS', 'SPECIALTY', 
                        'PRESENT_EMPLOYMENT_CODE', 'ADDR_STATUS', 'PHONE_STATUS', 'FAX_STATUS',
                        'SPEC_STATUS', 'PE_STATUS', 'NEW_METRIC', 'PPD_DATE', 'SOURCE']
    
    wslive_keep_cols_w_init = ['PHYSICIAN_ME_NUMBER', 'OFFICE_TELEPHONE', 'OFFICE_FAX', 'OFFICE_ADDRESS_LINE_2',  
                        'OFFICE_ADDRESS_LINE_1', 'OFFICE_ADDRESS_CITY', 'OFFICE_ADDRESS_STATE',  
                        'OFFICE_ADDRESS_ZIP', 
                        'INIT_POLO_MAILING_LINE_1', 'INIT_POLO_MAILING_LINE_2', 'INIT_POLO_CITY',
                        'INIT_POLO_STATE', 'INIT_POLO_ZIP', 'INIT_TELEPHONE_NUMBER', 'INIT_FAX_NUMBER',
                        'INIT_SAMPLE_MAX_PERFORM_MONTH', 'INIT_SAMPLE_SENT_MONTH', 'INIT_SAMPLE_DATE',
                        'WSLIVE_FILE_DT', 'WS_MONTH', 'COMMENTS', 'SPECIALTY', 
                        'PRESENT_EMPLOYMENT_CODE', 'ADDR_STATUS', 'PHONE_STATUS', 'FAX_STATUS',
                        'SPEC_STATUS', 'PE_STATUS', 'NEW_METRIC', 'PPD_DATE', 'SOURCE']

    # TODO: This should be part of the cleaning stage so we have standardized input data
    wslive_df = wslive.standardize(wslive_df)

    wslive_uniq_df = wslive.most_recent_by_me_number(wslive_df)
    
    if 'INIT_POLO_MAILING_LINE_2' in list(wslive_uniq_df.columns.values):
        wslive_uniq_df = wslive_uniq_df[wslive_keep_cols_w_init]
    else:
        wslive_uniq_df = wslive_uniq_df[wslive_keep_cols]

    wslive_ppd_df = wslive_uniq_df.merge(ppd_df, how='inner',
                                         left_on='PHYSICIAN_ME_NUMBER',  right_on='ME')

    return wslive_ppd_df


def create_wslive_ppd_data(wslive_df, ppd_file_lst):
    
    wslive_df = rename_wslive_init_smpl_cols(wslive_df)
    
    wslive_df['WS_MONTH'] = wslive_df['WS_MONTH'].astype(str)  
   
    wslive_ppd_df = None
    for i in range(len(ppd_file_lst)):
        ppd_file = ppd_file_lst[i]
        temp_ppd_df = pd.read_csv(ppd_file, delimiter=",", index_col=None, header=0, dtype=str)
        
        under_ndx = under_ndx = [i for i in range(len(ppd_file)) if ppd_file.startswith('_', i)]
        dot_ndx = ppd_file.find('.')
        ppd_date_str = ppd_file[under_ndx[-1] + 1:dot_ndx]
            
        ppd_date = datetime.datetime.strptime(ppd_date_str, '%Y%m%d')
        ppd_month = int(ppd_date.month)
        
        temp_wslive_df = wslive_df[wslive_df['INIT_SAMPLE_SENT_MONTH'] == ppd_month]
        temp_wslive_df['PPD_DATE'] = ppd_date
        
        if temp_wslive_df.shape[0] > 0:
            if not isinstance(wslive_ppd_df, pd.DataFrame):
                wslive_ppd_df = get_wslive_ppd_res_data(temp_wslive_df, temp_ppd_df)
            else:
                temp_df = get_wslive_ppd_res_data(temp_wslive_df, temp_ppd_df)
                wslive_ppd_df = pd.concat([wslive_ppd_df, temp_df], axis = 0, ignore_index = True)
                
    return wslive_ppd_df


def match_wslive_result_to_sample(wslive_uniq_me_res_df, init_sample_file_lst):
    
    for i in range(len(init_sample_file_lst)):
        temp_sample_file = init_sample_file_lst[i]
        temp_sample_df = pd.read_excel(temp_sample_file, index_col=None, header=0, dtype=str)
        temp_sample_df = df.rename_in_upper_case(temp_sample_df)
        
        slash_ndx = [i for i in range(len(temp_sample_file)) if temp_sample_file.startswith('/', i)]
        base_name = temp_sample_file[slash_ndx[-1] + 1:]
        under_ndx = base_name.find('_')
        dash_ndx = base_name.find('-')
        date_str = base_name[dash_ndx + 1:under_ndx]
        temp_sample_date = pd.to_datetime(date_str, format='%Y-%m-%d')
        
        temp_sample_df['SAMPLE_DATE'] = temp_sample_date
        
        init_month = int(temp_sample_date.month)
        temp_sample_df['SAMPLE_SENT_MONTH'] = init_month
        temp_sample_df['SAMPLE_MAX_PERFORM_MONTH'] = init_month + 2
        temp_sample_df['SAMPLE_DATE'] = temp_sample_date
        
    
        if i == 0:
            init_sample_df = temp_sample_df
        else:
            init_sample_df = pd.concat([init_sample_df, temp_sample_df], axis = 0, ignore_index = True)
                
    wslive_all_df = wslive_uniq_me_res_df.merge(init_sample_df, how='inner',
                                      left_on = 'PHYSICIAN_ME_NUMBER',  right_on ='ME')
    
    wslive_filter_df = wslive_all_df[wslive_all_df['WS_MONTH'].astype(int) <= wslive_all_df['SAMPLE_MAX_PERFORM_MONTH']]

    wslive_final_df = wslive_filter_df.sort_values('WSLIVE_FILE_DT', 
                            ascending = False).groupby('PHYSICIAN_ME_NUMBER').first().reset_index()

    return wslive_final_df


