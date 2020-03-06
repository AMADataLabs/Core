# Kari Palmier    Created 7/30/19
#
#############################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# Get path of general (common) code and add it to the python path variable
import sys
import os

# curr_path = os.path.abspath(__file__)
# slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
# base_path = curr_path[:slash_ndx[-2] + 1]
# gen_path = base_path + 'CommonModelCode\\'
# sys.path.insert(0, gen_path)

from get_entity_ppd_info import create_ent_comm_dates

import warnings

warnings.filterwarnings("ignore")


def convert_int_to_cat(data_df):
    cols_to_convert = ['ppd_top_cd', 'ppd_pe_cd', 'ppd_gender', 'ppd_region', 'ppd_division', 'ppd_group',
                       'ppd_micro_metro_ind', 'ppd_address_type', 'ppd_md_do_code', 'dpc', 'res', 'pcp',
                       'polo_ind', 'lic_state_match']

    for name in cols_to_convert:
        if name in list(data_df.columns.values):
            if sum(data_df[name].notnull()) > 0:
                data_df[name] = data_df[name].apply(
                    lambda x: round(int(x)) if ((x != None) and (~np.isnan(float(x)))) else x)
            data_df[name] = data_df[name].astype('category')

    return data_df


def convert_data_types(orig_data):
    print('CONVERT_DATA_TYPES')
    assert len(orig_data) > 0
    assert 'ent_comm_begin_dt' in orig_data
    print(orig_data.dtypes)
    orig_data = create_ent_comm_dates(orig_data, 'ent_comm_begin_dt')

    ent_no_end_ndx = orig_data['ent_comm_end_dt'].isna()
    orig_data.loc[ent_no_end_ndx, 'ent_comm_end_dt'] = datetime.datetime.now()
    orig_data = create_ent_comm_dates(orig_data, 'ent_comm_end_dt')

    orig_data['ppd_medschool_grad_year'] = pd.to_datetime(orig_data['ppd_medschool_grad_year'], format='%Y')
    orig_data['ppd_birth_year'] = pd.to_datetime(orig_data['ppd_birth_year'], format='%Y')

    col_names = list(orig_data.columns.values)
    for name in col_names:
        if str(orig_data[name].dtype) == 'object' or str(orig_data[name].dtype) == 'str':
            orig_data[name] = orig_data[name].astype('str')
            orig_data[name] = orig_data[name].str.upper()

            orig_data[name] = orig_data[name].apply(lambda x: x.upper() if isinstance(x, str) else x)
            orig_data[name] = orig_data[name].apply(lambda x: np.nan if x == 'NAN' else x)

    return orig_data


def clean_model_data(model_data, orig_data):
    model_cols = list(model_data.columns.values)

    # Replace NAN string from uppercase conversion back to NaN np float value
    for name in model_cols:
        if str(model_data[name].dtype) == 'object' or str(model_data[name].dtype) == 'category':
            NAN_ndx = model_data[name] == 'NAN'
            model_data.loc[NAN_ndx, name] = np.nan

            # Create dataframe of columns with NaN values and their NaN counts
    na_cnt = model_data.isna().sum()
    na_ndx = na_cnt > 0
    na_cnt_df = na_cnt[na_ndx]

    # Drop rows of any categorical variables that have NA/Null values (also drop from original data)
    # Replace any NA/Null numeric values with variable mean
    # Do not replace NaN values of variables with values of only 1 and 0 (are actually categorical)
    # Drop NaN rows of variables with only 0 ad 1 instead
    for name in na_cnt_df.index.values:
        if str(model_data[name].dtype) == 'object' or str(orig_data[name].dtype) == 'category':
            na_ndx = model_data[name].isna()
            model_data.drop(model_data[na_ndx].index, axis=0, inplace=True)
            orig_data.drop(orig_data[na_ndx].index, axis=0, inplace=True)
        elif str(model_data[name].dtype) == 'int64' or str(orig_data[name].dtype) == 'float64':
            if not (len(model_data[name].unique()) < 3 and \
                    ((0 in list(model_data[name].unique())) and (1 in list(model_data[name].unique())))):
                model_data[name] = model_data[name].astype('float64')
                model_data[name].fillna(model_data[name].mean(), inplace=True)
            else:
                na_ndx = model_data[name].isna()
                model_data.drop(model_data[na_ndx].index, axis=0, inplace=True)
                orig_data.drop(orig_data[na_ndx].index, axis=0, inplace=True)

    return model_data, orig_data


def create_explore_plots(model_data, fig_save_path):
    model_columns = list(model_data.columns.values)

    for i in range(len(model_columns)):
        if str(model_data[model_columns[i]].dtypes) == 'category' or str(
                model_data[model_columns[i]].dtypes) == 'object':
            model_data[model_columns[i]].value_counts().plot(kind='bar')
            plt.xlabel(model_columns[i])
            plt.ylabel('Count')
            plt.title(model_columns[i])
        else:
            temp_ndx = model_data[model_columns[i]].isnull()
            temp_var = model_data[model_columns[i]][~temp_ndx]

            plt.hist(temp_var, bins=20, alpha=0.5, edgecolor='black', linewidth=1.2)
            plt.xlabel(model_columns[i])
            plt.ylabel('Count')
            plt.title(model_columns[i])
            plt.grid(True)

        fig_path = fig_save_path + model_columns[i] + '.png'
        plt.savefig(fig_path)
        plt.close()


def create_new_phone_vars(orig_data):
    ###### Create new independent variable with 1 if person is licensed in wslive/ppd code state, 0 otherwise
    lic_state_match = np.zeros((orig_data.shape[0], 1))
    lic_ndx = orig_data['lic_match'] == 'Y'
    lic_state_match[lic_ndx] = 1
    orig_data['lic_state_match'] = lic_state_match

    ###### Create new independent variable with 1 if person is licensed in area code state, 0 otherwise
    if 'area_match' in list(orig_data.columns.values):
        area_state_match = np.zeros((orig_data.shape[0], 1))
        area_ndx = orig_data['area_match'] == 'Y'
        area_state_match[area_ndx] = 1
        orig_data['area_state_match'] = area_state_match

    ###### Create new independent variable with 1 if PPD type of practice ppd_top_cd is 020
    # (direct patient care DPC), otherwise 0
    dpc = np.zeros((orig_data.shape[0], 1))
    dpc_ndx = (orig_data['ppd_top_cd'] == '20') | (orig_data['ppd_top_cd'] == '020') | \
              (orig_data['ppd_top_cd'] == 20)
    dpc[dpc_ndx] = 1
    orig_data['dpc'] = dpc

    ###### Create new independent variable with 1 if PPD type of practice ppd_top_cd is 012 (resident),
    # otherwise 0
    res = np.zeros((orig_data.shape[0], 1))
    res_ndx = (orig_data['ppd_top_cd'] == '12') | (orig_data['ppd_top_cd'] == '012') | \
              (orig_data['ppd_top_cd'] == 12)
    res[res_ndx] = 1
    orig_data['res'] = res

    ###### Create new independent variable with 0 if ppd POLO mailing address is null, 1 if not null
    polo_ind = np.ones((orig_data.shape[0], 1))
    polo_ndx = orig_data['ppd_polo_mailing_line_2'].isna()
    polo_ind[polo_ndx] = 0
    orig_data['polo_ind'] = polo_ind

    ###### Create new independent variable with 1 if specialty is type of primary care, 0 otherwise
    prim_care_types = ["ADL", "AMF", "AMI", "FM", "FP", "GP", "GYN", "IM", "OBG", "OBS", "PD"]
    pcp = np.zeros((orig_data.shape[0], 1))
    pcp_ndx = orig_data['ppd_prim_spec_cd'].isin(prim_care_types)
    pcp[pcp_ndx] = 1
    orig_data['pcp'] = pcp

    ###### Create new independent variable with numeric values assigned based on src_cat_code (base case is 8)
    phone_src = np.ones((orig_data.shape[0], 1)).astype('int') * 8
    src_ndx1 = orig_data['ent_comm_src_cat_code'] == "VHCP"
    src_ndx2 = orig_data['ent_comm_src_cat_code'] == "WEBPHYC"
    src_ndx3 = orig_data['ent_comm_src_cat_code'] == "WEBVRTR"
    src_ndx4 = orig_data['ent_comm_src_cat_code'] == "PHNSURV"
    src_ndx5 = orig_data['ent_comm_src_cat_code'] == "GROUP"
    src_ndx6 = orig_data['ent_comm_src_cat_code'] == "NPI"
    src_ndx7 = orig_data['ent_comm_src_cat_code'] == "PHONE-CALL"

    phone_src[src_ndx1] = 1
    phone_src[src_ndx2] = 2
    phone_src[src_ndx3] = 3
    phone_src[src_ndx4] = 4
    phone_src[src_ndx5] = 5
    phone_src[src_ndx6] = 6
    phone_src[src_ndx7] = 7

    orig_data['phone_src'] = phone_src
    orig_data['phone_src'] = orig_data['phone_src'].astype('category')

    ###### Create new independent variable with representing how old each phone number is
    current_time = datetime.datetime.now()
    curr_time_df = pd.DataFrame(np.zeros((orig_data.shape[0], 1)), columns=['time'],
                                index=orig_data.index.values)
    curr_time_df['time'] = current_time

    yrs_old = (curr_time_df['time'] - orig_data['ent_comm_begin_dt']).apply(lambda x: x.days) / 365
    phone_age = np.ones((orig_data.shape[0], 1)).astype('int') * 4

    age_ndx1 = yrs_old < 1
    age_ndx2 = (1 <= yrs_old) & (yrs_old < 3)
    age_ndx3 = (3 <= yrs_old) & (yrs_old <= 5)

    phone_age[age_ndx1] = 1
    phone_age[age_ndx2] = 2
    phone_age[age_ndx3] = 3

    orig_data['phone_age_yrs'] = yrs_old
    orig_data['phone_age'] = phone_age
    orig_data['phone_age'] = orig_data['phone_age'].astype('category')

    ###### Create new independent variable with representing how long doctor has been practicing
    yop_yrs = (curr_time_df['time'] - orig_data['ppd_medschool_grad_year']).apply(lambda x: x.days) / 365
    yop = np.ones((orig_data.shape[0], 1)).astype('int') * 4

    yop_ndx1 = yop_yrs < 5
    yop_ndx2 = (5 <= yop_yrs) & (yop_yrs < 10)
    yop_ndx3 = (10 <= yop_yrs) & (yop_yrs <= 15)

    yop[yop_ndx1] = 1
    yop[yop_ndx2] = 2
    yop[yop_ndx3] = 3

    orig_data['yop_yrs'] = yop_yrs
    orig_data['yop'] = yop
    orig_data['yop'] = orig_data['yop'].astype('category')

    ###### Create new independent doctor age variable
    doctor_age_yrs = (curr_time_df['time'] - orig_data['ppd_birth_year']).apply(lambda x: x.days) / 365
    orig_data['doctor_age_yrs'] = doctor_age_yrs

    orig_data = convert_int_to_cat(orig_data)

    return orig_data


def create_new_addr_vars(orig_data):
    ###### Create new independent variable with 1 if license state matches PPD data state, 0 otherwise
    # lic_state_match = np.zeros((orig_data.shape[0], 1))
    # lic_ndx = orig_data['lic_match'] == 'Y'
    # lic_state_match[lic_ndx] = 1
    # orig_data['lic_state_match'] = lic_state_match

    # wtf is this above? was giving me an error on joins. "data must be 1-dimensional". WHY MAKE AN INDEX TO OVERWRITE
    # ZEROS, JUST DO IT LIKE THIS. Also, the create_new_phone_vars will also probably have the same error.
    orig_data['lic_state_match'] = orig_data['lic_match'].apply(lambda x: 1 if x == 'Y' else 0)  # fixed by Garrett

    ###### Create new independent variable with 1 if PPD type of practice ppd_top_cd is 020
    # (direct patient care DPC), otherwise 0
    # dpc = np.zeros((orig_data.shape[0], 1))
    # dpc_ndx = (orig_data['ppd_top_cd'] == '20') | (orig_data['ppd_top_cd'] == '020') | \
    #    (orig_data['ppd_top_cd'] == 20)
    # dpc[dpc_ndx] = 1
    # orig_data['dpc'] = dpc

    orig_data['dpc'] = orig_data['ppd_top_cd'].apply(lambda x: 1 if x in ['20', '020', 20] else 0)  # fixed by Garrett

    ###### Create new independent variable with 1 if PPD type of practice ppd_top_cd is 012 (resident),
    # otherwise 0
    # res = np.zeros((orig_data.shape[0], 1))
    # res_ndx = (orig_data['ppd_top_cd'] == '12') | (orig_data['ppd_top_cd'] == '012') | \
    #    (orig_data['ppd_top_cd'] == 12)
    # res[res_ndx] = 1
    # orig_data['res'] = res

    orig_data['res'] = orig_data['ppd_top_cd'].apply(lambda x: 1 if x in ['12', '012', 12] else 0)

    ###### Create new independent variable with 1 if specialty is type of primary care, 0 otherwise
    # prim_care_types = ["ADL", "AMF", "AMI", "FM", "FP", "GP", "GYN", "IM", "OBG", "OBS", "PD"]
    # pcp = np.zeros((orig_data.shape[0], 1))
    # pcp_ndx = orig_data['ppd_prim_spec_cd'].isin(prim_care_types)
    # pcp[pcp_ndx] = 1
    # orig_data['pcp'] = pcp

    orig_data['pcp'] = orig_data['ppd_prim_spec_cd'].apply(lambda x: 1 if x in ["ADL", "AMF", "AMI", "FM", "FP", "GP",
                                                                                "GYN", "IM", "OBG", "OBS", "PD"] else 0)

    ###### Create new independent variable with representing how old each address is
    current_time = datetime.datetime.now()
    curr_time_df = pd.DataFrame(np.zeros((orig_data.shape[0], 1)), columns=['time'],
                                index=orig_data.index.values)
    curr_time_df['time'] = current_time

    orig_data['addr_age_yrs'] = (pd.to_datetime(curr_time_df['time']) - pd.to_datetime(
        orig_data['ent_comm_begin_dt'])).apply(lambda x: x.days) / 365

    ###### Create new independent variable with representing how long doctor has been practicing
    orig_data['yop_yrs'] = (pd.to_datetime(curr_time_df['time']) - pd.to_datetime(
        orig_data['ppd_medschool_grad_year'])).apply(lambda x: x.days) / 365

    ###### Create new independent doctor age variable
    orig_data['doctor_age_yrs'] = (pd.to_datetime(curr_time_df['time']) - pd.to_datetime(
        orig_data['ppd_birth_year'])).apply(lambda x: x.days) / 365

    orig_data = convert_int_to_cat(orig_data)

    return orig_data

