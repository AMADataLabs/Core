# Kari Palmier    8/20/19    Created
#
#############################################################################
import pandas as pd
import datetime

import warnings

warnings.filterwarnings("ignore")

# Get path of general (common) code and add it to the python path variable
import sys
import os

# curr_path = os.path.abspath(__file__)
# slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
# base_path = curr_path[:slash_ndx[-2] + 1]
# gen_path = base_path + 'CommonModelCode\\'
# sys.path.insert(0, gen_path)

from rename_entity_cols import rename_post_cols, rename_comm_cols, rename_usg_cols
from rename_entity_cols import rename_phn_cols, rename_fone_zr_cols


def assign_lic_end_dates(license_df):
    null_inact_ndx = license_df['lic_exp_dt'].isna() & license_df['lic_rnw_dt'].isna() & \
                     license_df['lic_sts'].isin(['I', 'X', 'D'])
    lic_notnull_df = license_df[~null_inact_ndx]

    lic_notnull_df['anlys_end_dt'] = lic_notnull_df['lic_exp_dt']
    end_null_ndx = lic_notnull_df['anlys_end_dt'].isna()
    lic_notnull_df.loc[end_null_ndx, 'anlys_end_dt'] = lic_notnull_df.loc[end_null_ndx, 'lic_rnw_dt']

    lic_no_end_ndx = lic_notnull_df['anlys_end_dt'].isna()
    lic_notnull_df.loc[lic_no_end_ndx, 'anlys_end_dt'] = datetime.datetime.now()
    lic_notnull_df['anlys_end_dt'] = pd.to_datetime(lic_notnull_df['anlys_end_dt'], errors='coerce')
    lic_notnull_df = lic_notnull_df[lic_notnull_df['anlys_end_dt'].notnull()]

    lic_notnull_df['lic_issue_dt'] = pd.to_datetime(lic_notnull_df['lic_issue_dt'], errors='coerce')
    lic_notnull_df = lic_notnull_df[lic_notnull_df['lic_issue_dt'].notnull()]

    return lic_notnull_df


#### made by Garrett, attempting to simplify date cleaning process (commented block of code in create_ent_comm_dates below)
###def clean_date(text):
###    if not isinstance(text, str):
###        return text
###
###    if 'null' in text or text == '.':
###        return datetime.datetime.now()
###
###    invalids = '[]().,'
###    result = []
###    for c in text:
###        if c not in invalids:
###            result.append(c)
###    result = ''.join(result)
###
###    try:
###        result = pd.to_datetime(result)  # might throw error
###        return result
###    except:
###        return datetime.datetime.now()


def create_ent_comm_dates(orig_data, date_var):
    print('CREATE_ENT_COMM_DATES')
    ###assert len(orig_data) > 0
    ###orig_data[date_var] = orig_data[date_var].replace('.', datetime.datetime.now())
    ###orig_data[date_var] = orig_data[date_var].astype('str')
    ###orig_data[date_var] = orig_data[date_var].apply(lambda x: x[0:10] \
    ###         if x.find('-') > 0 else x[0:9])
    ###
    ###orig_data[date_var] = orig_data[date_var].apply(lambda x: pd.to_datetime(x, format = '%Y-%m-%d') \
    ###         if x.find('-') > 0 else pd.to_datetime(x, format = '%d%b%Y'))
    ###return orig_data
    print('cleaning date - {}'.format(date_var))
    #orig_data[date_var] = orig_data[date_var].apply(lambda x: cleannnnnnnnn_date(x))
    orig_data[date_var].fillna(datetime.datetime.now(), inplace=True)
    orig_data[date_var] = pd.to_datetime(orig_data[date_var])
    print('done cleaning date')
    assert len(orig_data) > 0
    return orig_data


def set_entity_dates(ent_data_df, begin_var, end_var):
    print('SET_ENTITY_DATES')
    assert len(ent_data_df) > 0
    print(begin_var)
    #ent_data_df = create_ent_comm_dates(ent_data_df, begin_var)
    ent_data_df[begin_var] = pd.to_datetime(ent_data_df[begin_var])

    #ent_no_end_ndx = ent_data_df[end_var].isna()
    #ent_data_df.loc[ent_no_end_ndx, end_var] = datetime.datetime.now()

    ent_data_df[end_var].fillna(datetime.datetime.now(), inplace=True)

    print(end_var)
    #ent_data_df = create_ent_comm_dates(ent_data_df, end_var)
    ent_data_df[end_var] = pd.to_datetime(ent_data_df[end_var])
    print('END SET_ENTITY_DATES')
    return ent_data_df


def rename_ent_ppd_addr_cols(data_df):
    ppd_rename_dict = {'POLO_MAILING_LINE_1': 'ORIG_POLO_MAILING_LINE_1',
                       'POLO_MAILING_LINE_2': 'ORIG_POLO_MAILING_LINE_2', 'POLO_CITY': 'ORIG_POLO_CITY',
                       'POLO_STATE': 'ORIG_POLO_STATE', 'POLO_ZIP': 'ORIG_POLO_ZIP'}
    data_df = data_df.rename(columns=ppd_rename_dict)

    ent_to_ppd_dict = {'post_addr_line1': 'POLO_MAILING_LINE_1',
                       'post_addr_line2': 'POLO_MAILING_LINE_2', 'post_city_cd': 'POLO_CITY',
                       'post_state_cd': 'POLO_STATE', 'post_zip': 'POLO_ZIP'}
    data_df = data_df.rename(columns=ent_to_ppd_dict)

    return data_df


def create_general_key(data_df, var1, var2, key_var):
    data_df = data_df[data_df[var1].notnull()]
    data_df[var1] = data_df[var1].astype(str)

    data_df = data_df[data_df[var2].notnull()]
    data_df[var2] = data_df[var2].astype(str)

    data_df[key_var] = data_df[var1].map(str) + '-' + data_df[var2].map(str)

    return data_df


def clean_addr_data(post_addr_df):
    post_addr_cols = ['comm_id', 'addr_line2', 'addr_line1', 'addr_line0', 'city_cd',
                      'state_cd', 'zip', 'plus4']
    post_addr_df = post_addr_df[post_addr_cols]
    post_addr_df = rename_post_cols(post_addr_df)

    post_addr_df = post_addr_df[(post_addr_df['post_addr_line2'].notnull()) &
                                (post_addr_df['post_city_cd'].notnull()) &
                                (post_addr_df['post_state_cd'].notnull()) &
                                (post_addr_df['post_zip'].notnull())]
    assert len(post_addr_df) > 0
    return post_addr_df


def clean_ent_comm_data(ent_comm_df):
    ent_comm_cols = ['entity_id', 'comm_type', 'begin_dt', 'comm_id', 'end_dt', 'src_cat_code']
    ent_comm_df = ent_comm_df[ent_comm_cols]
    ent_comm_df = rename_comm_cols(ent_comm_df)
    return ent_comm_df


def clean_email_data(ent_comm_df):
    ent_comm_cols = ['comm_id', 'user_nm', 'domain']
    ent_comm_df = ent_comm_df[ent_comm_cols]
    ent_comm_df = rename_comm_cols(ent_comm_df)

    return ent_comm_df


def clean_ent_usg_data(ent_usg_df):
    ent_usg_cols = ['entity_id', 'comm_type', 'comm_usage', 'usg_begin_dt', 'comm_id', 'comm_type',
                    'end_dt', 'src_cat_code']
    ent_usg_df = ent_usg_df[ent_usg_cols]
    ent_usg_df = rename_usg_cols(ent_usg_df)

    return ent_usg_df


def create_ent_me_data(ent_key_df):
    ent_me_df = ent_key_df[ent_key_df['key_type'] == 'ME']
    ent_me_df = ent_me_df.rename(columns={'key_type_val': 'ent_me'})

    return ent_me_df


def clean_phn_data(phone_df):
    phone_cols = ['comm_id', 'area_cd', 'exchange', 'phone_nbr']
    phone_df = phone_df[phone_cols]
    phone_df = rename_phn_cols(phone_df)

    phone_df = phone_df[(phone_df['phn_area_cd'].notnull()) &
                        (phone_df['phn_exchange'].notnull()) &
                        (phone_df['phn_phone_nbr'].notnull())]

    phone_df['aims_phone'] = phone_df['phn_area_cd'].astype(str) + \
                             phone_df['phn_exchange'].astype(str) + \
                             phone_df['phn_phone_nbr'].astype(str)

    return phone_df


def clean_fone_zr_data(fone_zr_df):
    fone_zr_cols = ['AREA_CD', 'STATE_CD', 'FIPS_CD', 'ZIP_CODE1', 'ZIP_CODE2', 'ZIP_CODE3']
    fone_zr_df = fone_zr_df[fone_zr_cols]
    fone_zr_df = rename_fone_zr_cols(fone_zr_df)

    fone_zr_df = fone_zr_df.drop_duplicates(subset=['FNZR_AREA_CD', 'FNZR_STATE_CD'])

    return fone_zr_df



