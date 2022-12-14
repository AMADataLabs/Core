""" Functions for business logic filtering of Address Model POLO updates """
# pylint: disable=import-error
from datetime import datetime
import logging
import re
import pandas as pd


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pylint: disable=anomalous-backslash-in-string, invalid-name
def remove_ste(street_address):
    text = re.sub('\W+', ' ', str(street_address).upper()).strip()
    tokens = text.split()
    ste_idx = None
    if 'STE' in tokens:
        ste_idx = tokens.index('STE')

    res = []
    for i, t in enumerate(tokens):
        if ste_idx is not None and i in (ste_idx, ste_idx + 1):  # ignore "STE" and next token
            pass
        else:
            res.append(t)
    return ' '.join(res)


# eventually move this to query the humach results archive database when it's stable and deployed
def get_recent_verified_me_address_keys(within_days=365, from_date=datetime.now(), data=None):
    if data is None:
        LOGGER.info('LOADING WSLIVE DATA')
        # wslive_path = "U:/Source Files/Data Analytics/Derek/SAS_DATA/SURVEY/wslive_results.sas7bdat"
        wslive_path = "C:\\Users\\Garrett\\Documents\\AMA\\humach\\wslive_results_sas.txt"
        # data = pd.read_sas(wslive_path, encoding='LATIN1')
        data = pd.read_csv(wslive_path, sep='|', dtype=str).fillna('')
    for col in data.columns:
        data[col] = data[col].fillna('').astype(str).apply(lambda x: ' '.join(x.split()).strip())

    data = data[
        [
            'PHYSICIAN_ME_NUMBER',
            'OFFICE_ADDRESS_LINE_1',
            'OFFICE_ADDRESS_LINE_2',
            'OFFICE_ADDRESS_ZIP',
            'COMMENTS',
            'OFFICE_ADDRESS_VERIFIED_UPDATED',
            'WSLIVE_FILE_DT'
        ]
    ]
    LOGGER.info('TRIMMING WSLIVE RESULTS')
    # filter to time frame
    if not isinstance(from_date, datetime):
        from_date = pd.to_datetime(from_date, errors='coerce')
    data['WSLIVE_FILE_DT'] = pd.to_datetime(data['WSLIVE_FILE_DT'], errors='coerce')
    data['time_diff'] = from_date - data['WSLIVE_FILE_DT']
    data['time_diff'] = data['time_diff'].apply(lambda x: x.days)
    data = data[data['time_diff'] <= within_days]

    # filter to verified results
    completed_call_comments = ['COMPLETE', 'RESPONDED TO SURVEY - AMA']

    def is_verified_address(comment, verified_updated):
        return comment in completed_call_comments and verified_updated in ['1', '2']  # 1 = verified, 2 = updated

    data['verified'] = [
        is_verified_address(c, v) for c, v in zip(
            data['COMMENTS'].apply(str.strip), data['OFFICE_ADDRESS_VERIFIED_UPDATED'].fillna('').astype(str).apply(str.strip)
        )
    ]
    data = data[data['verified'] == True]
    del data['verified']

    # make key
    data['PHYSICIAN_ME_NUMBER'] = data['PHYSICIAN_ME_NUMBER'].apply(lambda x: ('0000000' + str(x))[-11:])
    data['me_address_key'] = data['PHYSICIAN_ME_NUMBER'] + '_' + \
                             data['OFFICE_ADDRESS_LINE_2'].apply(remove_ste) + '_' + \
                             data['OFFICE_ADDRESS_ZIP']

    verified_me_address_keys = data['me_address_key'].drop_duplicates()
    LOGGER.info(f'VERIFIED ADDRESSES: {len(verified_me_address_keys)}')
    return verified_me_address_keys


# specify ppd_path to match ppd version with same ppd used to find model application population. None -> get latest
def get_polo_address_scores(data: pd.DataFrame, ppd=None) -> pd.DataFrame:
    """
    data: scored data with columns
    ['me', 'entity_id', 'comm_id', 'addr_line0', 'addr_line1', 'addr_line2', 'city_cd', 'state_cd', 'zip', 'score']
    """

    # use PPD to find existing POLOs
    #ppd = load_expanded_ppd(path=ppd_path)
    if ppd is None:
        ppd = pd.read_csv('C:\\Users\\Garrett\\Documents\\AMA\\ppd\\ppd_analysis_file.csv', dtype=str)

    ppd = ppd[['ME', 'ENTITY_ID', 'POLO_COMM_ID']].rename(
        columns={
            'ME': 'me',
            'ENTITY_ID': 'entity_id',
            'POLO_COMM_ID': 'comm_id'
        }
    )
    print(data.columns.values)
    print(data.head(1))
    # safe-guards on data type for matching
    ppd['me'] = ppd['me'].apply(lambda x: ('000000000' + str(x))[-11:])
    data['me'] = data['me'].apply(lambda x: ('000000000' + str(x))[-11:])
    # ppd['entity_id'] = ppd['entity_id'].astype(str)
    # data['entity_id'] = data['entity_id'].astype(str)
    ppd['comm_id'] = ppd['comm_id'].astype(str)
    data['comm_id'] = data['comm_id'].astype(str)
    # add scores for PPDs
    ppd = ppd.drop(columns='entity_id', axis=1).merge(
        data,
        # on=['me', 'entity_id', 'comm_id'],
        on=['me', 'comm_id'],
        how='inner'
    )

    # add 'polo_' prefix for later comparison
    ppd.rename(
        columns={
            'comm_id': 'polo_comm_id',
            'address_key': 'polo_address_key',
            'addr_line0': 'polo_addr_line0',
            'addr_line1': 'polo_addr_line1',
            'addr_line2': 'polo_addr_line2',
            'city_cd': 'polo_city_cd',
            'state_cd': 'polo_state_cd',
            'zip': 'polo_zip',
            'score': 'polo_score'
        }, inplace=True
    )
    return ppd


# top-scoring data
def get_bolo_addresses(data: pd.DataFrame) -> pd.DataFrame:
    """
    data: scored model output, unique by (entity_id, comm_id)
    """
    print(data.columns.values)
    return data.sort_values(by='score', ascending=False).groupby('entity_id').first().reset_index()


def get_bolo_vs_polo_data(bolo_data: pd.DataFrame, polo_data: pd.DataFrame) -> pd.DataFrame:
    # standardize joining column
    bolo_data['me'] = bolo_data['me'].astype(str).apply(lambda x: ('00000' + x)[-11:])
    polo_data['me'] = polo_data['me'].astype(str).apply(lambda x: ('00000' + x)[-11:])

    data = bolo_data.merge(
        polo_data.drop(columns=['entity_id'], axis=1),
        on='me',
        how='left'
    )
    data = data[
        (~data['comm_id'].isna()) &
        # (~data['polo_comm_id'].isna()) &
        (data['comm_id'] != data['polo_comm_id']) &
        (data['address_key'] != data['polo_address_key'])
    ]
    return data


def filter_on_score_difference(bolo_polo_data: pd.DataFrame, difference_threshold: float) -> pd.DataFrame:
    """
    difference_threshold: range from 0-1

    returns: data for which the best office address is rated AT LEAST <difference_threshold> higher than POLO
    """
    LOGGER.info(f'FILTERING TO SCORE DIFFERENCE THRESHOLD OF {difference_threshold}')
    LOGGER.info(f'PRE-FILTER: {len(bolo_polo_data)}')
    data = bolo_polo_data[
        bolo_polo_data['score'].astype(float) - bolo_polo_data['polo_score'].astype(float) >= difference_threshold
    ]
    LOGGER.info(f'POST-FILTER: {len(data)}')
    return data

def filter_recent_verified_addresses(
        bolo_polo_data: pd.DataFrame,
        within_days: int,
        from_date=datetime.now(),
        verified_addresses=None):
    """ We don't want to overwrite recently-verified POLOs so we remove those verified addresses from candidates """
    LOGGER.info('FILTERING OUT RECENTLY-VALIDATED ME-ADDRESS PAIRS')
    # get recently-verified address data
    if verified_addresses is None:
        verified_addresses = get_recent_verified_me_address_keys(within_days=within_days, from_date=from_date)

    # make key from me + address_key or me + addr_line2 + zip if necessary
    if 'address_key' in bolo_polo_data.columns.values:
        bolo_polo_data['me_polo_address_key'] = bolo_polo_data['me'].astype(str) + '_' + bolo_polo_data['address_key'].fillna('')
    else:
        bolo_polo_data['me_polo_address_key'] = \
            bolo_polo_data['me'] + '_' + \
            bolo_polo_data['addr_line2'].apply(remove_ste) + '_' + \
            bolo_polo_data['zip']

    bolo_polo_data['me_polo_address_key'] = bolo_polo_data['me_polo_address_key'].apply(str.upper)
    #print(bolo_polo_data['me_polo_address_key'].values[:10])
    #print(verified_addresses[:10])

    LOGGER.info(f'PRE-FILTER: {len(bolo_polo_data)}')
    unverified = bolo_polo_data[~bolo_polo_data['me_polo_address_key'].isin(verified_addresses)]
    LOGGER.info(f'POST-FILTER: {len(unverified)}')
    return unverified
