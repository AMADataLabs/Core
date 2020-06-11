from datetime import datetime
import numpy as np
import pandas as pd
import string

import logging
logging.basicConfig(level=logging.INFO)

from datalabs.access.aims import AIMS
from datalabs.common import excel
from datalabs.messaging.outlook import Outlook

import settings

logger = logging.getLogger('info')

TODAY_DATE = str(datetime.now().date())

AMC_QUERY_FILE = 'query_amc_data.sql'
FLAG_WORD_FILE = 'U:/Source Files/Data Analytics/Data-Science/Data/AMC_Address_Sweep/AMC_flag_words.xlsx'
OUTPUT_DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/AMC_Address_Sweep/output'
OUTPUT_FILE = f'{OUTPUT_DIRECTORY}/AMC_flagged_addresses_{TODAY_DATE}.xlsx'
OUTPUT_FILE_PASSWORD = 'Survey20'

REPORT_SENDER = 'DataLabs@ama-assn.org'
REPORT_RECIPIENTS = ['Nicole.Neal@ama-assn.org',
                     'Debbie.Kidd@ama-assn.org',
                     'Christina.Lopez@ama-assn.org',
                     'Sandeep.Dhamale@ama-assn.org']
REPORT_CC = ['Garrett.Lappe@ama-assn.org']

# valid addresses might otherwise be flagged looking for flag words 'mail', 'stop'
FALSE_POSITIVES = ['sebastopol',
                   'mail stop',
                   'mail code',
                   'mailstop',
                   'mail center',
                   'mail slot',
                   'mail box',
                   'mailslot',
                   'mail ctr',
                   'vanderbilt mail']


def get_flag_words():
    flag_words = pd.read_excel(FLAG_WORD_FILE, header=None)[0].values
    flag_words = [str(word).lower() for word in flag_words]

    print(flag_words)
    return flag_words


def get_amc_address_data():
    with open(AMC_QUERY_FILE, 'r') as f:
        sql = f.read()
    with AIMS() as aims:
        data = aims.read(sql=sql, coerce_float=False)

    data = clean_str_data(data)
    return data


def is_flagged_city(city_string):
    city_string = city_string.lower()
    return any([city_string == '',
                len(set(city_string)) == 1,
                any([d in city_string for d in string.digits])])


def is_flagged_addr1(addr1_string, flag_null=False):
    flag = False

    if not flag_null:
        if addr1_string is not None and len(addr1_string) != 0:
            addr1_string = addr1_string.lower()
            # if address only contains 1 unique character
            if len(set(addr1_string)) <= 1:
                flag = True

    if flag_null:
        if addr1_string is None or len(addr1_string) == 0 or addr1_string == '':
            flag = True
    return flag


# addr_line_2 is typically street address--the major address component, so integers are not allowed
def is_flagged_addr2(addr2_string):
    flag = False

    # if null or empty
    if addr2_string is None or len(addr2_string) == 0:
        flag = True

    # if addr2 is a digit or has <= 2 unique characters
    elif len(set(addr2_string)) <= 2 or addr2_string.isdigit():
        flag = True

    return flag


def is_flagged_state(state_string):
    # if null, not 2 characters, not 2 unique characters, any non-ascii letters
    return any([state_string is None,
                all([len(state_string) != 2, any([not isinstance(c, str) for c in state_string])]),
                len(set(state_string.lower())) != 2,
                any([c not in string.ascii_letters for c in state_string])])


def is_flagged_zip(zip_string):
    flag = False

    if zip_string is None:
        flag = True

    # if any non-digits or len > 5
    if any([any([c not in string.digits for c in zip_string]),
            len(zip_string) > 5]):
        flag = True

    return flag


def contains_flagword(address_string, flag_words):
    address_string = address_string.lower()

    # we want to avoid false positive markers from flagging the method that checks for flag words.
    # this is done by removing the text of false positives from the aggregated address text before
    # we search that text for flag words.
    for fp in FALSE_POSITIVES:
        if fp in address_string:
            address_string = address_string.replace(fp, '')

    tokens = address_string.split()

    return any([t in flag_words for t in tokens])


def clean_str_data(data: pd.DataFrame):
    data.fillna('', inplace=True)
    data.replace(np.nan, '', inplace=True, regex=True)

    for col in data.columns.values:
        data[col] = data[col].astype(str).apply(lambda x: x.strip())

    data['address'] = data['addr_line0'].str.lower() + ' ' + \
                      data['addr_line1'].str.lower() + ' ' + \
                      data['addr_line2'].str.lower() + ' ' + \
                      data['city_cd'].str.lower() + ' ' + \
                      data['state_cd'].str.lower()
    data['usg_begin_dt'] = data['usg_begin_dt'].apply(lambda x: x.replace('[', '').replace(']', ''))
    data['usg_begin_dt'] = data['usg_begin_dt'].apply(lambda x: x[:x.index(':')] if ':' in x else x)
    data['usg_begin_dt'] = pd.to_datetime(data['usg_begin_dt'])

    return data


def get_flagged_data_and_summary(data):
    logger.info('\tAdding flag indicator columns:')
    logger.info('\t\taddr1')
    data['addr1_flagged'] = data['addr_line1'].apply(lambda x: is_flagged_addr1(x))
    logger.info('\t\taddr2')
    data['addr2_flagged'] = data['addr_line2'].apply(lambda x: is_flagged_addr2(x))
    logger.info('\t\tcity')
    data['city_flagged'] = data['city_cd'].apply(lambda x: is_flagged_city(x))
    logger.info('\t\tstate')
    data['state_flagged'] = data['state_cd'].apply(lambda x: is_flagged_state(x))
    logger.info('\t\tzip')
    data['zip_flagged'] = data['zip'].apply(lambda x: is_flagged_zip(x))

    flag_words = get_flag_words()
    logger.info('\t\tflagwords')
    data['contains_flag_word'] = data['address'].apply(lambda x: contains_flagword(x, flag_words))

    logger.info('\tGetting flag type counts.')

    # flag type ounts
    n_addr1     = len(data[data['addr1_flagged']])
    n_addr2     = len(data[data['addr2_flagged']])
    n_city      = len(data[data['city_flagged']])
    n_state     = len(data[data['state_flagged']])
    n_zip       = len(data[data['zip_flagged']])
    n_flagwords = len(data[data['contains_flag_word']])

    flags = {
        'addr_line1': n_addr1,
        'addr_line2': n_addr2,
        'city': n_city,
        'state': n_state,
        'zip': n_zip,
        'flag_word': n_flagwords}

    # compile records that have any flag
    logger.info('\tCompiling flagged Records.')
    any_flags = []
    for i, row in data.iterrows():
        a = any([row['addr1_flagged'],
                 row['addr2_flagged'],
                 row['city_flagged'],
                 row['state_flagged'],
                 row['zip_flagged'],
                 row['contains_flag_word']])
        any_flags.append(a)

    data['any_flag'] = any_flags
    results_summary = ''
    results_summary += f"Count of all flagged AMC-sourced addresses:{len(data[data['any_flag']])}"
    results_summary += '\nFlagging summary: (addresses can be flagged by multiple fields, ' \
                       'so the sum of these could exceed count above)'
    for f in flags:
        val = flags[f]
        if val > 0:
            results_summary += '\n\t{}: {}'.format(f, val)

    data.drop(columns='address', axis=1, inplace=True)  # delete temp column

    flagged_data = data[data['any_flag']]
    flagged_data.drop(columns='any_flag', axis=1, inplace=True)  # drop redundant column (all values are True)

    flagged_data['date_checked'] = TODAY_DATE

    return flagged_data, results_summary


def save_output(data: pd.DataFrame):
    output_file = f'{OUTPUT_DIRECTORY}/AMC_flagged_addresses_{TODAY_DATE}.xlsx'

    excel.save_formatted_output(data, output_file, 'AMC Address Sweep')
    excel.add_password_to_xlsx(output_file, OUTPUT_FILE_PASSWORD)


def run_amc_flagging_script():
    logger.info('Querying active AMC-sourced address data.')
    data = get_amc_address_data()
    logger.info('Cleaning data.')
    data = clean_str_data(data)

    flagged_data, summary = get_flagged_data_and_summary(data)
    logger.info('Saving results.')
    save_output(flagged_data)

    logger.info('Creating email report.')
    report_body = \
    'Hello!\n\n' + \
    'Attached are the latest results of the AMC address flagging script.\n\n' + \
    'Password: Survey20\n\n' + \
    'Results summary:\n' + \
    summary + \
    '\n\nThis report and email were generated automatically.\n' + \
    'If you believe there are errors or if you have questions or suggestions, please contact Garrett.\n\n' + \
    'Thanks!'

    outlook = Outlook()
    outlook.send_email(to=REPORT_RECIPIENTS,
                       cc=REPORT_CC,
                       subject=f'AMC Sweep Results - {TODAY_DATE}',
                       body=report_body,
                       from_account=REPORT_SENDER,
                       attachments=[OUTPUT_FILE],
                       auto_send=False)


if __name__ == '__main__':
    run_amc_flagging_script()
