# Kari Palmier    9/20/19    Created
#
#############################################################################
import datetime
import os
import sys

import pandas as pd

from   datalabs.access.ppd import PPDFile
from   datalabs.access.sample import SampleFile
import datalabs.curate.wslive as wslive

from get_wslive_res_init_ppd_info import create_wslive_ppd_data

from rename_model_cols import rename_ppd_columns
from get_entity_ppd_info import assign_lic_end_dates, create_general_key


def get_ent_phn_counts(ent_data, group_var_lst, count_var_name):
    
    ent_count_df = ent_data.groupby(group_var_lst).size().reset_index()
    ent_count_df = ent_count_df.rename(columns = {0:count_var_name})
    keep_vars = group_var_lst
    keep_vars.append(count_var_name)
    ent_count_df = ent_count_df[keep_vars]
    
    return ent_count_df
    
  
def create_combined_phn_ent_data(ent_df, phone_df, ent_join_var, phn_join_var):

    entity_phn_df = ent_df.merge(phone_df,
                                 how='inner',
                                 left_on=ent_join_var,
                                 right_on=phn_join_var)
    
    return entity_phn_df


def get_ent_counts(entity_phn_df, id_phn_var, all_phn_var, ent_id_var, phone_var):
    
    ent_id_phn_count_df = get_ent_phn_counts(entity_phn_df, [ent_id_var, phone_var], id_phn_var)
    ent_all_phn_count_df = get_ent_phn_counts(entity_phn_df, [phone_var], all_phn_var)
    
    return ent_id_phn_count_df, ent_all_phn_count_df


def create_ent_comm_data(ent_comm_df, phone_df, ent_key_df, phone_var):
    
    entity_phn_df = create_combined_phn_ent_data(ent_comm_df, phone_df, 'ent_comm_comm_id', 
                                                 'phn_comm_id')
    
    hist_ent_id_phn_count_df, hist_ent_all_phn_count_df = get_ent_counts(entity_phn_df, 
                                                                         'hist_ent_id_phn_count',
                                                                         'hist_ent_all_phn_count',
                                                                         'ent_comm_entity_id',
                                                                         phone_var)
    
    entity_phn_df = entity_phn_df.merge(ent_key_df,
                                        how='inner',
                                        left_on='ent_comm_entity_id',
                                        right_on='entity_id')
    
    return entity_phn_df, hist_ent_id_phn_count_df, hist_ent_all_phn_count_df


def create_ent_usg_data(ent_comm_usg_df, phone_df, ent_key_df, phone_var):
    
    entity_usg_phn_df = create_combined_phn_ent_data(ent_comm_usg_df, phone_df, 'usg_comm_id', 'phn_comm_id')
        
    hist_usg_id_phn_count_df, hist_usg_all_phn_count_df = get_ent_counts(entity_usg_phn_df, 
                                                                         'hist_usg_id_phn_count',
                                                                         'hist_usg_all_phn_count',
                                                                         'usg_entity_id',
                                                                         phone_var)
       
    entity_usg_phn_df = entity_usg_phn_df.merge(ent_key_df,
                                                how='inner',
                                                left_on='usg_entity_id',
                                                right_on='entity_id')
    
    return entity_usg_phn_df, hist_usg_id_phn_count_df, hist_usg_all_phn_count_df


def get_valid_ppd_ent_data(ent_ppd_df, date_var):

    ent_ppd_df['ent_comm_begin_dt'] = pd.to_datetime(ent_ppd_df['ent_comm_begin_dt'])
    ent_ppd_df['ent_comm_end_dt'].fillna(datetime.datetime.now(), inplace=True)
    ent_ppd_df['ent_comm_end_dt'] = pd.to_datetime(ent_ppd_df['ent_comm_end_dt'])

    ent_date_df = ent_ppd_df[(ent_ppd_df['ent_comm_begin_dt'] <= ent_ppd_df[date_var]) &
                             (ent_ppd_df['ent_comm_end_dt'] >= ent_ppd_df[date_var])]
              
    return ent_date_df


def get_valid_ppd_usg_data(usg_df, date_var):

    usg_df['usg_begin_dt'] = pd.to_datetime(usg_df['usg_begin_dt'])
    usg_df['usg_end_dt'].fillna(datetime.datetime.now(), inplace=True)
    usg_df['usg_end_dt'] = pd.to_datetime(usg_df['usg_end_dt'])

    usg_date_df = usg_df[(usg_df['usg_begin_dt'] <= usg_df[date_var]) & \
                                              (usg_df['usg_end_dt'] >= usg_df[date_var])]

    return usg_date_df


def join_ent_comm_count_data(ent_date_df, ent_id_phn_count_df, ent_all_phn_count_df, 
                        id_phn_var, all_phn_var, phone_var):
    
    ent_date_df = ent_date_df.merge(ent_id_phn_count_df,
                                    how='left',
                                    on=['ent_comm_entity_id', phone_var])
    ent_date_df = ent_date_df.merge(ent_all_phn_count_df,
                                    how='left',
                                    on=[phone_var])
    
    ent_date_df.loc[ent_date_df[id_phn_var].isna(), id_phn_var] = 0
    ent_date_df.loc[ent_date_df[all_phn_var].isna(), all_phn_var] = 0
    
    return ent_date_df
    

def join_ent_usg_count_data(ent_date_df, ent_id_phn_count_df, ent_all_phn_count_df, 
                        id_phn_var, all_phn_var, phone_var):
    
    ent_date_df = ent_date_df.merge(ent_id_phn_count_df,
                                    how='left',
                                    left_on=['ent_comm_entity_id', phone_var],
                                    right_on=['usg_entity_id', phone_var])

    ent_date_df = ent_date_df.drop(['usg_entity_id'], axis=1)
    ent_date_df = ent_date_df.merge(ent_all_phn_count_df,
                                    how='left',
                                    on=phone_var)
    
    ent_date_df.loc[ent_date_df[id_phn_var].isna(), id_phn_var] = 0
    ent_date_df.loc[ent_date_df[all_phn_var].isna(), all_phn_var] = 0

    return ent_date_df


def get_ent_lic_data(ent_date_df, license_df, date_var, state_var):
    
    lic_notnull_df = assign_lic_end_dates(license_df)
    
    lic_ent_dt_df = lic_notnull_df.merge(ent_date_df[['ent_comm_entity_id', date_var]],
                                         how='inner',
                                         left_on='entity_id',
                                         right_on='ent_comm_entity_id')
    
    license_date_df = lic_ent_dt_df[(lic_ent_dt_df['lic_issue_dt'] <= lic_ent_dt_df[date_var]) &
                                    (lic_ent_dt_df['anlys_end_dt'] >= lic_ent_dt_df[date_var])]
    
    lic_filter_df = license_date_df[license_date_df['entity_id'].isin(list(ent_date_df['ent_comm_entity_id'].unique()))]
        
    
    ent_lic_df = create_general_key(ent_date_df, 'entity_id', state_var, 'ent_phn_lic_key')
    lic_filter_df = create_general_key(lic_filter_df, 'entity_id', 'state_cd', 'act_lic_key')
    
    ent_lic_df['lic_match'] = 'N'
    lic_ndx = ent_lic_df['ent_phn_lic_key'].isin(lic_filter_df['act_lic_key'])
    ent_lic_df.loc[lic_ndx, 'lic_match'] = 'Y'
    
    return ent_lic_df, lic_filter_df


def get_fone_lic_data(ent_date_df, fone_zr_df, lic_filter_df):
    
    fone_ent_dt_df = ent_date_df.merge(fone_zr_df,
                                       how='inner',
                                       left_on='phn_area_cd',
                                       right_on='FNZR_AREA_CD')
    
    ent_fone_df = create_general_key(fone_ent_dt_df, 'entity_id', 'FNZR_STATE_CD', 'ent_fone_key')
    
    ent_fone_df['area_match'] = 'N'
    lic_ndx = ent_fone_df['ent_fone_key'].isin(lic_filter_df['act_lic_key'])
    ent_fone_df.loc[lic_ndx, 'area_match'] = 'Y'
    
    return ent_fone_df


def create_phn_entity_data(ent_comm_df, ent_comm_usg_df, phone_df, ent_key_df,
                           date_df, date_var, date_me_var):

    entity_phn_df, hist_ent_id_phn_count_df, hist_ent_all_phn_count_df = \
        create_ent_comm_data(ent_comm_df, phone_df, ent_key_df, 'aims_phone')


    entity_usg_phn_df, hist_usg_id_phn_count_df, hist_usg_all_phn_count_df = \
        create_ent_usg_data(ent_comm_usg_df, phone_df, ent_key_df, 'aims_phone')
    
        
    entity_phn_df = entity_phn_df.merge(date_df,
                                        how='inner',
                                        left_on='ent_me',
                                        right_on=date_me_var)

    entity_phn_df = get_valid_ppd_ent_data(entity_phn_df, date_var)
      
    curr_ent_id_phn_count_df, curr_ent_all_phn_count_df = get_ent_counts(entity_phn_df, 
                                                                         'curr_ent_id_phn_count',
                                                                         'curr_ent_all_phn_count',
                                                                         'ent_comm_entity_id',
                                                                         'aims_phone')

        
    entity_usg_phn_df = entity_usg_phn_df.merge(date_df,
                                                how='inner',
                                                left_on='ent_me',
                                                right_on=date_me_var)

    entity_usg_phn_df = get_valid_ppd_usg_data(entity_usg_phn_df, date_var)
       
    curr_usg_id_phn_count_df, curr_all_usg_phn_count_df = get_ent_counts(entity_usg_phn_df, 
                                                                         'curr_usg_id_phn_count',
                                                                         'curr_usg_all_phn_count',
                                                                         'usg_entity_id',
                                                                         'aims_phone')

    
    entity_phn_df = join_ent_comm_count_data(entity_phn_df, hist_ent_id_phn_count_df, 
                                             hist_ent_all_phn_count_df, 'hist_ent_id_phn_count',
                                             'hist_ent_all_phn_count', 'aims_phone')
    
    entity_phn_df = join_ent_comm_count_data(entity_phn_df, curr_ent_id_phn_count_df, 
                                             curr_ent_all_phn_count_df, 'curr_ent_id_phn_count',
                                             'curr_ent_all_phn_count', 'aims_phone')
    
    entity_phn_df = join_ent_usg_count_data(entity_phn_df, hist_usg_id_phn_count_df, 
                                             hist_usg_all_phn_count_df, 'hist_usg_id_phn_count',
                                             'hist_usg_all_phn_count', 'aims_phone')
    
    entity_phn_df = join_ent_usg_count_data(entity_phn_df, curr_usg_id_phn_count_df, 
                                             curr_all_usg_phn_count_df, 'curr_usg_id_phn_count',
                                             'curr_usg_all_phn_count', 'aims_phone')
        
    return entity_phn_df


def create_model_initial_data(wslive_uniq_me_res_df, init_sample_file_lst, ppd_file_lst, ent_comm_df, 
                              ent_comm_usg_df, phone_df, license_df, ent_key_df, fone_zr_df):
    samples = SampleFile.load_multiple(init_sample_file_lst)
    wslive_uniq_res_init_df = wslive_uniq_me_res_df.wslive.match_to_samples(samples)
    
    ppds = PPDFile.load_multiple(ppd_file_lst)
    wslive_ppd_df = wslive_uniq_res_init_df.wslive.match_to_ppds(ppds)

    date_df =  wslive_ppd_df[['ME', 'INIT_SAMPLE_DATE']]

    entity_df = create_phn_entity_data(ent_comm_df, ent_comm_usg_df, 
                                       phone_df, ent_key_df,
                                       date_df, 'INIT_SAMPLE_DATE', 'ME')
    
    entity_df = entity_df.drop(['INIT_SAMPLE_DATE', 'ME'], axis=1)
    
    wslive_ent_ppd_df = wslive_ppd_df.merge(entity_df,
                                            how='inner',
                                            left_on='ME',
                                            right_on='ent_me')
    
    wslive_ent_ppd_df, lic_filter_df = get_ent_lic_data(wslive_ent_ppd_df, license_df, 'INIT_SAMPLE_DATE', 'INIT_POLO_STATE')
    
    wslive_ent_ppd_df = get_fone_lic_data(wslive_ent_ppd_df, fone_zr_df, lic_filter_df)
    
    wslive_final_df = rename_ppd_columns(wslive_ent_ppd_df)
    
    return wslive_final_df


def create_ppd_scoring_data(ppd_df, ppd_date, ent_comm_df, ent_comm_usg_df, phone_df, 
                            license_df, ent_key_df, fone_zr_df):
 
    ppd_df = ppd_df[(ppd_df['TELEPHONE_NUMBER'].notnull())]
    ppd_df = ppd_df[(ppd_df['TOP_CD'] == '020') |
                    (ppd_df['TOP_CD'] == '20') |
                    (ppd_df['TOP_CD'] == 20)]
    
    ppd_df['ppd_date'] = ppd_date
    
    date_df = ppd_df[['ME', 'ppd_date']]

    entity_df = create_phn_entity_data(ent_comm_df, ent_comm_usg_df, 
                                       phone_df, ent_key_df,
                                       date_df, 'ppd_date', 'ME')
    
    entity_df = entity_df.drop(['ppd_date', 'ME'], axis=1)
    
    ent_ppd_df = ppd_df.merge(entity_df,
                              how='inner',
                              left_on='ME',
                              right_on='ent_me')
    
    ent_ppd_df, lic_filter_df = get_ent_lic_data(ent_ppd_df, license_df, 'ppd_date', 'POLO_STATE')
    
    ent_ppd_df = get_fone_lic_data(ent_ppd_df, fone_zr_df, lic_filter_df)
    
    ppd_final_df = rename_ppd_columns(ent_ppd_df)

    return ppd_final_df


