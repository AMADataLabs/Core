# Kari Palmier    9/20/19    Created
#
#############################################################################
import warnings

warnings.filterwarnings("ignore")

# Get path of general (common) code and add it to the python path variable
import sys
import os

from   datalabs.model.exception import BadDataFrameMerge

# curr_path = os.path.abspath(__file__)
# slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
# base_path = curr_path[:slash_ndx[-2] + 1]
# gen_path = base_path + 'CommonCode\\'
# sys.path.insert(0, gen_path)

from capitalize_df_contents import capitalize_df_contents
from get_wslive_res_init_ppd_info import match_wslive_result_to_sample, create_wslive_ppd_data

# gen_path = base_path + 'CommonModelCode\\'
# sys.path.insert(0, gen_path)

from rename_model_cols import rename_ppd_columns
from rename_entity_cols import rename_comm_cols

from get_entity_ppd_info import set_entity_dates, assign_lic_end_dates, create_general_key
from get_entity_ppd_info import clean_ent_comm_data, clean_addr_data, clean_ent_usg_data
from get_entity_ppd_info import create_ent_me_data


# returns df of records without addresses with PO box
def get_non_po_box(data_df, addr_var_list):
    po_regex_strs = 'P.O.|P.O. |PO |P O|BOX | APT |POBOX|LOCKBOX|MAILBOX|LOCK BOX|MAIL BOX'

    data_df = capitalize_df_contents(data_df)

    for var in addr_var_list:
        po_ndx = data_df[var].str.contains(po_regex_strs, na=False, regex=True)
        data_df = data_df[~po_ndx]

    return data_df


# returns df of records with POLO eligible addresses
def get_polo_eligible(entity_data_df, addr_var_list):
    print('GET_POLO_ELIGIBLE')
    assert len(entity_data_df) > 0

    eligible_comm_types = ['OF', 'HO', 'GROUP']
    eligible_comm_srcs = ['AMC', 'GROUP', 'MBSHP-WEB', 'PHONE-CALL', '	PPA', 'WHITE-MAIL', 'E-MAIL',
                          'MBSHP-MAIL', 'OLDCC', 'PHNSURV', 'USC-OUTBND', 'CME-REG', '	LOCK_BOX',
                          'MBSHP-PHON', 'MBSHP-PURL', 'OUTREACH', 'REQ-CARDS', 'RES-TIPON',
                          'WEBSURV', '	BATCH', 'YELLOW', '	DEA', 'NPI', 'ACS', 'ACXIOMNCOA', '	LIST-HOUSE',
                          'NCOA', '	OTHER', 'POLO', 'PPMA', 'PRFSOL', 'MFLOAD', 'OBSOLETE', 'ADDR-VER',
                          'FAST-TRACK', 'PUBS', 'RETURNED', 'WEB', 'ACXIOM', 'ACXIOMLODE', 'ACXIOMPLUS',
                          'ADMIT-HOS', 'ADVR', 'AFFIL-GRP', 'AMA-ORG', 'CGMT', 'CGMT-EXC', 'COA-PS',
                          'ECF-CNVRSN', 'ECI', 'FEDERATION', 'GME', 'INTERACT', 'INTERNET', 'MBSHP-',
                          'MBSHP-OTHR', 'MRKT-RSRCH', 'PER', 'PPS', 'ROSTER', 'SCHL-HOSP', 'STU-MATRIC',
                          'UNKNOWN', '	MEDEC', 'ACXIOM-DSF']

    # entity_data_df['ent_comm_comm_type'] = entity_data_df['ent_comm_comm_type'].apply(str.strip)
    # entity_data_df['ent_comm_src_cat_code'] = entity_data_df['ent_comm_src_cat_code'].apply(str.strip)

    entity_data_polo_df = entity_data_df[entity_data_df['ent_comm_comm_type'].isin(eligible_comm_types) & \
                                         entity_data_df['ent_comm_src_cat_code'].isin(eligible_comm_srcs)]
    assert len(entity_data_polo_df) > 0

    entity_data_polo_df = get_non_po_box(entity_data_polo_df, addr_var_list)
    assert len(entity_data_polo_df) > 0

    return entity_data_polo_df


def create_addr_key(data_df, addr_var, zip_var, st_num_var, addr_key_var):
    print('CREATE_ADDR_KEY')
    assert len(data_df) > 0
    data_df = data_df[data_df[addr_var].notnull()]
    assert len(data_df) > 0
    data_df[addr_var] = data_df[addr_var].astype(str)
    data_df = data_df[data_df[zip_var].notnull()]
    assert len(data_df) > 0
    data_df[zip_var] = data_df[zip_var].astype(str)
    data_df[st_num_var] = data_df[addr_var].apply(
        lambda x: x[0:(x.find(' '))] if x[0:(x.find(' '))].isnumeric() else '')
    data_df = data_df[data_df[st_num_var] != '']
    assert len(data_df) > 0
    data_df[addr_key_var] = data_df[st_num_var].map(str) + '-' + data_df[zip_var].map(str)
    assert len(data_df) > 0
    return data_df


def get_ent_addr_counts(ent_data, group_var_lst, count_var_name):
    # ent_data = entity_addr_df
    # group_var_lst = [ent_id_var, addr_key_var]    OR    [addr_key_var]
    # count_var_name = id_addr_var
    ent_count_df = ent_data.groupby(group_var_lst).size().reset_index()
    ent_count_df = ent_count_df.rename(columns={0: count_var_name})
    keep_vars = group_var_lst
    keep_vars.append(count_var_name)
    ent_count_df = ent_count_df[keep_vars]

    return ent_count_df


def create_combined_addr_ent_data(ent_df, post_addr_df, ent_join_var, st_num_var, addr_key_var):
    print('CREATE_COMBINED_ADDR_ENT_DATA')
    print('len ent_df:\t\t{}'.format(len(ent_df)))
    print(ent_df)
    print('len post_addr_df:\t\t{}'.format(len(post_addr_df)))
    print(post_addr_df)
    entity_addr_df = ent_df.merge(post_addr_df,
                                  how='inner', left_on=ent_join_var,
                                  right_on='post_comm_id')
    if entity_addr_df.empty:
        raise BadDataFrameMerge(f"No results returned from merge on variables '{ent_join_var}' and 'post_comm_id'.")

    print('len entity_addr_df:\t\t{}'.format(len(entity_addr_df)))
    entity_addr_df = create_addr_key(entity_addr_df, 'post_addr_line2', 'post_zip',
                                     st_num_var, addr_key_var)
    print('END CREATE_COMBINED_ADDR_ENT_DATA')
    return entity_addr_df


def get_ent_counts(entity_addr_df, id_addr_var, all_addr_var, ent_id_var, addr_key_var):
    # id_addr_var = 'curr_usg_id_addr_count',
    # all_addr_var = 'curr_usg_all_addr_count',
    # ent_id_var = 'usg_entity_id',
    # addr_key_var = 'usg_addr_key'

    ent_id_addr_count_df = get_ent_addr_counts(entity_addr_df, [ent_id_var, addr_key_var], id_addr_var)
    ent_all_addr_count_df = get_ent_addr_counts(entity_addr_df, [addr_key_var], all_addr_var)

    return ent_id_addr_count_df, ent_all_addr_count_df


def create_ent_comm_data(ent_comm_df, post_addr_df, ent_key_df):
    print("CREATE_ENT_COMM_DATA")
    entity_addr_df = create_combined_addr_ent_data(ent_comm_df, post_addr_df, 'ent_comm_comm_id',
                                                   'ent_st_num', 'ent_addr_key')
    assert 'ent_comm_begin_dt' in entity_addr_df.columns.values or 'begin_dt' in entity_addr_df.columns.values
    print('len entity_addr_df:\t\t{}'.format(len(entity_addr_df)))
    addr_var_list = ['post_addr_line0', 'post_addr_line1', 'post_addr_line2']
    entity_addr_df = get_polo_eligible(entity_addr_df, addr_var_list)
    print('len entity_addr_df:\t\t{}'.format(len(entity_addr_df)))
    assert 'ent_comm_begin_dt' in entity_addr_df.columns.values or 'begin_dt' in entity_addr_df.columns.values
    #entity_addr_df.to_csv('C:\\Users\\glappe\\Documents\\udrive\\Data\\Polo_Rank_Model\\_Archived\\entity_addr_df.csv')
    #quit()
    hist_ent_id_addr_count_df, hist_ent_all_addr_count_df = get_ent_counts(entity_addr_df,
                                                                           'hist_ent_id_addr_count',
                                                                           'hist_ent_all_addr_count',
                                                                           'ent_comm_entity_id',
                                                                           'ent_addr_key')

    entity_addr_df = entity_addr_df.merge(ent_key_df, how='inner', left_on='ent_comm_entity_id',
                                          right_on='entity_id')
    assert 'ent_comm_begin_dt' in entity_addr_df.columns.values or 'begin_dt' in entity_addr_df.columns.values
    return entity_addr_df, hist_ent_id_addr_count_df, hist_ent_all_addr_count_df


def create_ent_usg_data(ent_comm_usg_df, post_addr_df, ent_key_df):
    print('CREATE_ENT_USG_DATA')
    entity_usg_addr_df = create_combined_addr_ent_data(ent_comm_usg_df, post_addr_df, 'usg_comm_id',
                                                       'usg_st_num', 'usg_addr_key')
    assert len(entity_usg_addr_df) > 0
    hist_usg_id_addr_count_df, hist_usg_all_addr_count_df = get_ent_counts(entity_usg_addr_df,
                                                                           'hist_usg_id_addr_count',
                                                                           'hist_usg_all_addr_count',
                                                                           'usg_entity_id',
                                                                           'usg_addr_key')
    assert len(hist_usg_all_addr_count_df) > 0
    entity_usg_addr_df = entity_usg_addr_df.merge(ent_key_df, how='inner', left_on='usg_entity_id',
                                                  right_on='entity_id')
    assert len(entity_usg_addr_df) > 0
    return entity_usg_addr_df, hist_usg_id_addr_count_df, hist_usg_all_addr_count_df


def get_valid_ppd_ent_data(ent_ppd_df, date_var):
    print('GET_VALID_PPD_ENT_DATA')
    assert len(ent_ppd_df) > 0
    ent_ppd_df = set_entity_dates(ent_ppd_df, 'ent_comm_begin_dt', 'ent_comm_end_dt')

    ent_date_df = ent_ppd_df[(ent_ppd_df['ent_comm_begin_dt'] <= ent_ppd_df[date_var]) &
                             (ent_ppd_df['ent_comm_end_dt'] >= ent_ppd_df[date_var])]

    return ent_date_df

import pandas as pd
import datetime

def get_valid_ppd_usg_data(usg_df, date_var):
    print('GET_VALID_PPD_USG_DATA')
    print('date_var:', date_var)
    print('date:', usg_df[date_var])
    print('a. usg_df:', len(usg_df))
    usg_df = set_entity_dates(usg_df, 'usg_begin_dt', 'usg_end_dt')
    print('b. usg_df:', len(usg_df))

    assert len(usg_df) > 0

    usg_df['usg_begin_dt'] = pd.to_datetime(usg_df['usg_begin_dt'])
    usg_df['usg_end_dt'] = pd.to_datetime(usg_df['usg_end_dt']).fillna(datetime.datetime.now())
    usg_df[date_var] = pd.to_datetime(usg_df[date_var])

    print(usg_df['usg_begin_dt'].values[:5])
    print(usg_df['usg_end_dt'].values[:5])
    print(usg_df[date_var].values[:5])

    print('c. usg_df:', len(usg_df))
    usg_date_df = usg_df[(usg_df['usg_begin_dt'] <= usg_df[date_var]) &
                         (usg_df['usg_end_dt'] >= usg_df[date_var])]
    print('d. usg_df:', len(usg_df))
    assert len(usg_date_df) > 0
    return usg_date_df


def join_ent_comm_count_data(ent_date_df, ent_id_addr_count_df, ent_all_addr_count_df, id_addr_var, all_addr_var):
    print('JOIN_ENT_COMM_COUNT_DATA')
    match_cols = ['ent_comm_entity_id', 'ent_addr_key']
    for c in match_cols:
        ent_date_df[c] = ent_date_df[c].astype(str)
        ent_id_addr_count_df[c] = ent_id_addr_count_df[c].astype(str)
    assert len(ent_date_df) > 0
    ent_date_df = ent_date_df.merge(ent_id_addr_count_df,
                                    how='left',
                                    on=['ent_comm_entity_id', 'ent_addr_key'])
    assert len(ent_date_df) > 0
    ent_date_df = ent_date_df.merge(ent_all_addr_count_df,
                                    how='left',
                                    on=['ent_addr_key'])
    assert len(ent_date_df) > 0
    ent_date_df.loc[ent_date_df[id_addr_var].isna(), id_addr_var] = 0
    ent_date_df.loc[ent_date_df[all_addr_var].isna(), all_addr_var] = 0
    assert len(ent_date_df) > 0
    return ent_date_df


def join_ent_usg_count_data(ent_date_df, ent_id_addr_count_df, ent_all_addr_count_df,
                            id_addr_var, all_addr_var):
    print('JOIN_ENT_USG_COUNT_DATA')
    left_cols = ['ent_comm_entity_id', 'ent_addr_key']
    for c in left_cols:
        ent_date_df[c] = ent_date_df[c].astype(str)
    right_cols = ['usg_entity_id', 'usg_addr_key']
    for c in right_cols:
        ent_id_addr_count_df[c] = ent_id_addr_count_df[c].astype(str)

    ent_date_df = ent_date_df.merge(ent_id_addr_count_df,
                                    how='left',
                                    left_on=['ent_comm_entity_id', 'ent_addr_key'],
                                    right_on=['usg_entity_id', 'usg_addr_key'])

    ent_date_df.drop(['usg_entity_id', 'usg_addr_key'], axis=1, inplace=True)
    assert len(ent_date_df) > 0
    ent_date_df = ent_date_df.merge(ent_all_addr_count_df,
                                    how='left',
                                    left_on='ent_addr_key',
                                    right_on='usg_addr_key')
    ent_date_df.drop(['usg_addr_key'], axis=1, inplace=True)

    ent_date_df.loc[ent_date_df[id_addr_var].isna(), id_addr_var] = 0
    ent_date_df.loc[ent_date_df[all_addr_var].isna(), all_addr_var] = 0

    return ent_date_df


def get_ent_lic_data(ent_date_df, license_df, date_var):
    print('GET_ENT_LIC_DATA')
    lic_notnull_df = assign_lic_end_dates(license_df)
    assert len(lic_notnull_df) > 0
    lic_ent_dt_df = lic_notnull_df.merge(ent_date_df[['ent_comm_entity_id', date_var]],
                                         how='inner',
                                         left_on='entity_id',
                                         right_on='ent_comm_entity_id')
    assert len(lic_ent_dt_df) > 0
    license_date_df = lic_ent_dt_df[(lic_ent_dt_df['lic_issue_dt'] <= lic_ent_dt_df[date_var]) & \
                                    (lic_ent_dt_df['anlys_end_dt'] >= lic_ent_dt_df[date_var])]
    assert len(license_date_df) > 0
    lic_filter_df = license_date_df[license_date_df['entity_id'].isin(list(ent_date_df['ent_comm_entity_id'].unique()))]

    wslive_ent_lic_df = create_general_key(ent_date_df, 'entity_id', 'post_state_cd', 'ent_post_lic_key')
    lic_filter_df = create_general_key(lic_filter_df, 'entity_id', 'state_cd', 'act_lic_key')

    wslive_ent_lic_df['lic_match'] = 'N'
    lic_ndx = wslive_ent_lic_df['ent_post_lic_key'].isin(lic_filter_df['act_lic_key'])
    wslive_ent_lic_df.loc[lic_ndx, 'lic_match'] = 'Y'
    assert len(wslive_ent_lic_df) > 0
    assert 'ent_comm_begin_dt' in ent_date_df
    assert 'ent_comm_begin_dt' in wslive_ent_lic_df
    return wslive_ent_lic_df


def create_addr_entity_data(ent_comm_df, ent_comm_usg_df, post_addr_df, license_df, ent_key_df, date_df, date_var,
                            date_me_var):
    print('CREATE_ADDR_ENTITY_DATA')
    print('0. ent_comm_usg_df:', len(ent_comm_usg_df))
    assert len(ent_comm_df) > 0
    assert len(post_addr_df) > 0
    assert len(ent_comm_usg_df) > 0
    assert len(ent_key_df) > 0
    assert len(date_df) > 0
    print('\tCLEANING')
    # ent_comm_df = clean_ent_comm_data(ent_comm_df)
    # post_addr_df = clean_addr_data(post_addr_df)
    # ent_comm_usg_df = clean_ent_usg_data(ent_comm_usg_df)

    # ent_key_df['key_type'] = ent_key_df['key_type'].apply(str.strip)
    ent_key_df = create_ent_me_data(ent_key_df)

    print('len ent_comm_df:\t\t{}'.format(len(ent_comm_df)))
    print('len post_addr_df:\t\t{}'.format(len(post_addr_df)))
    print('len ent_comm_usg_df:\t\t{}'.format(len(ent_comm_usg_df)))
    print('len ent_key_df:\t\t{}'.format(len(ent_key_df)))
    assert len(ent_comm_df) > 0
    assert len(post_addr_df) > 0
    assert len(ent_comm_usg_df) > 0
    assert len(ent_key_df) > 0

    entity_addr_df, hist_ent_id_addr_count_df, hist_ent_all_addr_count_df = \
        create_ent_comm_data(ent_comm_df, post_addr_df, ent_key_df)
    assert 'ent_comm_begin_dt' in entity_addr_df.columns.values
    assert len(entity_addr_df) > 0

    entity_usg_addr_df, hist_usg_id_addr_count_df, hist_usg_all_addr_count_df = \
        create_ent_usg_data(ent_comm_usg_df, post_addr_df, ent_key_df)
    print('1. entity_usg_addr_df:', len(entity_usg_addr_df))
    assert len(entity_usg_addr_df) > 0
    assert len(hist_usg_id_addr_count_df) > 0
    assert len(hist_usg_all_addr_count_df) > 0

    print('merging entity_addr_df and date_df')
    print('entity_addr_df cols')
    print(entity_addr_df.dtypes)
    print()
    print('entity_addr_df cols')
    print(entity_addr_df.dtypes)
    entity_addr_df = entity_addr_df.merge(date_df, how='inner', left_on='ent_me', right_on=date_me_var)

    entity_addr_df = get_valid_ppd_ent_data(entity_addr_df, date_var)
    assert 'ent_comm_begin_dt' in entity_addr_df.columns.values

    curr_ent_id_addr_count_df, curr_ent_all_addr_count_df = get_ent_counts(entity_addr_df,
                                                                           'curr_ent_id_addr_count',
                                                                           'curr_ent_all_addr_count',
                                                                           'ent_comm_entity_id',
                                                                           'ent_addr_key')

    entity_usg_addr_df = entity_usg_addr_df.merge(date_df, how='inner', left_on='ent_me', right_on=date_me_var)
    print('2. entity_usg_addr_df:', len(entity_usg_addr_df))
    entity_usg_addr_df = get_valid_ppd_usg_data(entity_usg_addr_df, date_var)
    print('3. entity_usg_addr_df:', len(entity_usg_addr_df))
    # entity_usg_addr_df.to_csv('C:\\Users\\glappe\\Documents\\udrive\\Data\\Polo_Rank_Model\\_Archived\\entity_usg_addr_df.csv')
    # quit()
    curr_usg_id_addr_count_df, curr_all_usg_addr_count_df = get_ent_counts(entity_usg_addr_df,
                                                                           'curr_usg_id_addr_count',
                                                                           'curr_usg_all_addr_count',
                                                                           'usg_entity_id',
                                                                           'usg_addr_key')

    print('join_ent_comm_count_data - historical')
    entity_addr_df = join_ent_comm_count_data(entity_addr_df, hist_ent_id_addr_count_df,
                                              hist_ent_all_addr_count_df, 'hist_ent_id_addr_count',
                                              'hist_ent_all_addr_count')
    assert len(entity_addr_df) > 0
    print('join_ent_comm_count_data - current')
    entity_addr_df = join_ent_comm_count_data(entity_addr_df, curr_ent_id_addr_count_df,
                                              curr_ent_all_addr_count_df, 'curr_ent_id_addr_count',
                                              'curr_ent_all_addr_count')
    assert len(entity_addr_df) > 0
    print('join_ent_usg_count_data - historical')
    entity_addr_df = join_ent_usg_count_data(entity_addr_df, hist_usg_id_addr_count_df,
                                             hist_usg_all_addr_count_df, 'hist_usg_id_addr_count',
                                             'hist_usg_all_addr_count')
    assert len(entity_addr_df) > 0
    print('join_ent_usg_count_data - current')
    entity_addr_df = join_ent_usg_count_data(entity_addr_df, curr_usg_id_addr_count_df,
                                             curr_all_usg_addr_count_df, 'curr_usg_id_addr_count',
                                             'curr_usg_all_addr_count')
    assert len(entity_addr_df) > 0

    entity_addr_df = get_ent_lic_data(entity_addr_df, license_df, date_var)
    assert 'ent_comm_begin_dt' in entity_addr_df.columns.values
    assert len(entity_addr_df) > 0
    entity_addr_df = entity_addr_df.drop([date_var, date_me_var], axis=1)
    assert len(entity_addr_df) > 0
    entity_addr_df['ent_me'] = entity_addr_df['ent_me'].astype(str)
    return entity_addr_df


# creates data to be used by the pre-processing notebook (which is used to build and train models)
def create_model_initial_data(wslive_uniq_me_res_df, init_sample_file_lst, ppd_file_lst, ent_comm_df,
                              ent_comm_usg_df, post_addr_df, license_df, ent_key_df):
    wslive_uniq_res_init_df = match_wslive_result_to_sample(wslive_uniq_me_res_df, init_sample_file_lst)

    wslive_ppd_df = create_wslive_ppd_data(wslive_uniq_res_init_df, ppd_file_lst)

    date_df = wslive_ppd_df[['ME', 'INIT_SAMPLE_DATE']]

    entity_df = create_addr_entity_data(ent_comm_df, ent_comm_usg_df,
                                        post_addr_df, license_df, ent_key_df,
                                        date_df, 'INIT_SAMPLE_DATE', 'ME')

    wslive_ppd_df = create_addr_key(wslive_ppd_df, 'INIT_POLO_MAILING_LINE_2', 'INIT_POLO_ZIP',
                                    'INIT_SMPL_ST_NUM', 'INIT_SMPL_ADDR_KEY')

    wslive_ppd_df = create_addr_key(wslive_ppd_df, 'OFFICE_ADDRESS_LINE_2', 'OFFICE_ADDRESS_ZIP',
                                    'WSLIVE_ST_NUM', 'WSLIVE_ADDR_KEY')

    wslive_ent_ppd_df = wslive_ppd_df.merge(entity_df, how='inner', left_on='ME', right_on='ent_me')

    wslive_final_df = rename_ppd_columns(wslive_ent_ppd_df)

    return wslive_final_df


# creates data which the model is applied to
def create_ppd_scoring_data(ppd_df, ppd_date, ent_comm_df, ent_comm_usg_df, post_addr_df,
                            license_df, ent_key_df):
    print('CREATE_PPD_SCORING_DATA')

    print('len ppd_df:\t\t{}'.format(len(ppd_df)))
    print('len ent_comm_df:\t\t{}'.format(len(ent_comm_df)))
    print('len ent_comm_usg_df:\t\t{}'.format(len(ent_comm_usg_df)))
    print('len post_addr_df:\t\t{}'.format(len(post_addr_df)))
    print('len license_df:\t\t{}'.format(len(license_df)))
    print('len ent_key_df:\t\t{}'.format(len(ent_key_df)))
    assert len(ppd_df) > 0
    assert len(ent_comm_df) > 0
    assert len(ent_comm_usg_df) > 0
    assert len(post_addr_df) > 0
    assert len(license_df) > 0
    assert len(ent_key_df) > 0

    ppd_df['ME'] = ppd_df['ME'].astype(str)
    print()
    print('len ppd_df:\t\t{}'.format(len(ppd_df)))
    print('removing records with null line2, state, or zip')
    # remove records with null line 2, state, or zip
    ppd_df = ppd_df[(ppd_df['POLO_MAILING_LINE_2'].notnull()) &
                    (ppd_df['POLO_STATE'].notnull()) &
                    (ppd_df['POLO_ZIP'].notnull())]
    print('len ppd_df:\t\t{}'.format(len(ppd_df)))

    print('trimming to dpc')
    ppd_df = ppd_df[(ppd_df['TOP_CD'] == '020') | (ppd_df['TOP_CD'] == '20') | (ppd_df['TOP_CD'] == 20)]
    assert len(ppd_df) > 0
    print('len ppd_df:\t\t{}'.format(len(ppd_df)))

    ppd_df['ppd_date'] = ppd_date

    date_df = ppd_df[['ME', 'ppd_date']]

    print('creating addr_entity_data')
    print('#######################################################')
    print('begin_dt ent_comm_begin_dt in...')
    print('ent_comm_df')
    print('\tent_comm_begin_dt', 'ent_comm_begin_dt' in ent_comm_df.columns.values)
    print('\tbegin_dt', 'begin_dt' in ent_comm_df.columns.values)
    #print('ent_comm_usg_df')
    #print('\tent_comm_begin_dt', 'ent_comm_begin_dt' in ent_comm_usg_df.columns.values)
    #print('\tbegin_dt', 'begin_dt' in ent_comm_usg_df.columns.values)

    entity_df = create_addr_entity_data(ent_comm_df, ent_comm_usg_df,
                                        post_addr_df, license_df, ent_key_df,
                                        date_df, 'ppd_date', 'ME')
    print('entity_df')
    print('\tent_comm_begin_dt', 'ent_comm_begin_dt' in entity_df.columns.values)
    print('\tbegin_dt', 'begin_dt' in entity_df.columns.values)
    assert any(['begin_dt' in entity_df.columns.values, 'ent_comm_begin_dt' in entity_df.columns.values])
    assert len(entity_df) > 0
    ppd_df = create_addr_key(ppd_df, 'POLO_MAILING_LINE_2', 'POLO_ZIP',
                             'PPD_ST_NUM', 'PPD_ADDR_KEY')

    entity_df['ent_me'] = entity_df['ent_me'].astype(str)  #### was "entity_df = entity_df['ent_me'].astype(str)"
    assert len(entity_df) > 0

    assert 'ent_comm_begin_dt' in entity_df.columns.values

    ent_ppd_df = ppd_df.merge(entity_df, how='inner', left_on='ME', right_on='ent_me')
    assert len(ent_ppd_df) > 0

    assert 'ent_comm_begin_dt' in ent_ppd_df.columns.values

    ppd_final_df = rename_ppd_columns(ent_ppd_df)
    #ppd_final_df = rename_comm_cols(ppd_final_df)
    assert len(ppd_final_df) > 0
    for col in ppd_final_df.columns.values:
        print(col)
    print('ent_comm_begin_dt:', 'ent_comm_begin_dt' in ppd_final_df.columns.values)
    print('begin_dt:', 'begin_dt' in ppd_final_df.columns.values)

    assert 'ent_comm_begin_dt' in ppd_final_df.columns.values
    return ppd_final_df


