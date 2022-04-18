import json
import pandas as pd
from pprint import pprint, pformat
import datetime
from dateutil.parser import parse
import sys
import os

# Configure the file to log to and the format of the message

""" This insert allows for the import below """
sys.path.insert(0, 'U:\\Source Files\\Data Analytics\\Data-Science\\Code-Library\\PPD\\')
import get_ppd  # used for generating the batch delete file (matching to MEs with disconnected phone numbers)

sys.path.insert(0, 'U:\\Source Files\\Data Analytics\\Data-Science\\Code-Library\\Common_Code\\')
from LoggingModule import *
set_log_file('rpv.log', format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_key = token = os.getenv("RPV_token")  # System environment variable with RPV token for auth

archive_path = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\RPV\output\\_archive\\RPV_archive.csv'
# global phonecol  # the name of the column with phone numbers
N_days_buffer = 10  # do not test any numbers that have been tested in the past N days.

endpoint = 'https://api.realvalidation.com/rpvWebService/RealPhoneValidationTurbo.php?output=json&'
auth = 'token={}'.format(API_key)

kill_statuses = [
    'unreachable',
    'restricted',
    'unauthorized',
    'server-unavailable']  # a status in this list is not immediately resolvable--halt loop.


# TODO expand this phone validation method using Kari's logic

# returns whether input 10-digit number (or string of number) not starting with 0 and with more than 2 unique digits
def is_valid_phone(phone):
    phone = str(phone)
    return len(phone) == 10 and phone.isdigit() and phone[0] != '0' and len(set(phone)) > 2


# attempts to infer the name of the column storing phone number
def determine_phone_colname(df):
    # possible column names for phone number column
    phone_columns = ['OFFICE_TELEPHONE',
                     'TELEPHONE_NUMBER',
                     'PHONE_NUMBER',
                     'PHONE',
                     'NUMBER',
                     'PPD_TELEPHONE_NUMBER',
                     'TELEPHONE',
                     'TELEPHONE NUMBER',
                     'PHONE NUMBER',
                     'OFFICE TELEPHONE']
    phone_columns.extend([i.lower() for i in phone_columns])

    assert any([colname in phone_columns for colname in
                df]), 'Error: DataFrame must have phone column with one of the following names (ignoring case): {}' \
        .format(phone_columns[:int(len(phone_columns) / 2)])
    for colname in df:
        if colname.upper() in phone_columns:
            return colname


# return a list of unique phone numbers in the input DataFrame,
def get_unique_phones_list(df):
    try:
        phonecol = determine_phone_colname(df)
        phones = [p for p in df[phonecol].drop_duplicates()]
        return phones

    except Exception:
        logging.error("Error: DataFrame df not defined.")
        return -1  # will cause an error downstream.


# returns a DataFrame of the archived RPV results that were tested in the past n_days.
# n_days Defaults to N_days_buffer
def get_RPV_archive_df(n_days=N_days_buffer):
    date = datetime.datetime.now().date()

    # read archived RPV requests
    df_archive = pd.read_csv(archive_path)
    df_archive['phone'] = df_archive['phone'].astype(str)

    # reduce to archived results added in past N days
    df_archive = df_archive[
        df_archive['date_checked'].apply(lambda x: abs(date - parse(str(x)).date()).days <= n_days)]. \
        drop_duplicates()

    return df_archive


# This variable needs to be above the scope of get_RPV_result()
df_archive = get_RPV_archive_df()
archived_records = []


# get_RPV_result(phone) - returns a Series of the RPV result for a single phone number.
def get_RPV_result(phone, check_archive=True):

    phone = str(phone)
    # if the phone number is in the archive(default 10 days) don't re-test the number but re-use previous result.
    if check_archive and phone in [p for p in df_archive['phone']]:

        archived_records.append(phone)
        found_in_archive_msg = 'Phone {} found in recently-tested archive. Re-using previous result.'.format(phone)
        logging.info(found_in_archive_msg)
        old = df_archive[df_archive['phone'] == phone]  # access old record using phone as index

        # substitute new record with old result
        s = pd.DataFrame(
            [[phone, old['status'], old['error_text'], old['iscell'], old['carrier'], old['date_checked']]],
            columns=[c for c in df_archive.columns])

        return s  # , None
        # NO NEED TO ARCHIVE THIS RECORD BECAUSE IT ALREADY EXISTS, THAT'S WHY WE'RE HERE IN THE FIRST PLACE.

    # only make API call if phone is a 10-digit number or 10-character string of digits
    elif is_valid_phone(phone):
        # raise ValueError("Not supposed to be here")
        date = datetime.datetime.now().date()

        url = endpoint + auth + '&phone={}'.format(str(phone))
        response = requests.get(url)

        response_json = json.loads(response.content)

        if response.status_code == 200:

            # logging.DEBUG(pformat(response_json))  # debugging
            # Identify result fields
            status = response_json['status']
            error_text = response_json['error_text']
            iscell = response_json['iscell']
            carrier = response_json['carrier']

            # if status is is in kill_statuses, there is a major problem that must be resolved. Script canceled.
            if status in kill_statuses:
                error_msg = 'SCRIPT ERROR for phone {}. Status: {}'.format(phone, status)
                logging.error(error_msg)
                raise ValueError("Fatal RPV response status code")

            s = pd.DataFrame([[phone, status, error_text, iscell, carrier, date]],
                             columns=[c for c in df_archive.columns])

            # append the 1-row DF above to the archive CSV
            s.to_csv(archive_path, mode='a+', header=False, index=False)

            # return the Series (can be appended to a larger result DataFrame) and hte response JSON for logging
            return s  # , response_json

        # if there request was unsuccessful, record the response for that phone number and response
        else:
            logging.info(response.status_code)
            response_json = json.loads(response.content)
            logging.info(pformat(response_json))
            print()
            response_status_msg = phone + ' ' + response_json['status']
            logging.info(response_status_msg)
            print()
            raise ValueError('Error response code: {}'.format(response.status_code))
    # enf if


# process_list - main loop to send requests to RPV and collect responses
# phones: a list of phone numbers
# check_archive: boolean, whether or not we look in archive for recent results to avoid re-testing in some time window
def get_RPV_results_df(phones, check_archive=True):

    phones = list(set(phones))  # removing duplicates from list
    num_phones = len(phones)
    unique_phone_msg = 'Unique phone numbers to process: {}'.format(num_phones)
    logging.info(unique_phone_msg)

    df_archive = get_RPV_archive_df()
    df_archive['phone'] = df_archive['phone'].astype(str)

    # the fields that are contained in RPV's response JSON along with current date for logging purposes
    df_result = pd.DataFrame(columns=['phone', 'status', 'error_text', 'iscell', 'carrier', 'date_checked'])

    # request_log_dict = {}  # nothing is done with this at the moment.

    num_calls = 0

    for phone in phones:

        s = get_RPV_result(phone, check_archive)
        num_calls += 1

        # request_log_dict[phone] = response_json

        # append the series above to our overall results DataFrame
        df_result = df_result.append(s, ignore_index=True)

    num_archived = len(archived_records)  # print out the number of archived results found while processing this list.
    if num_archived > 0:
        log_msg = '{} number'.format(num_archived) + ('s' if num_archived > 1 else '') + 'from list found in archived RPV results from past {} days.'.format(N_days_buffer)
        logging.info(log_msg)

    return df_result


# "main" method
# given a path to an input file, send API request to RPV for each number and get results.
# check_archive: boolean, whether or not we look in archive for recent results to avoid re-testing in some time window
def process_batch(df=None, check_archive=True, batch_del=False):

    final_cols = [c for c in df.columns]  # columns in input file
    final_cols.extend(['status', 'error_text', 'iscell', 'carrier', 'date_checked'])  # columns of RPV results

    logging.info('Processing batch.')
    number_of_records_msg = 'Number of records: {}'.format(len(df))
    logging.info(number_of_records_msg)


    phonecol = determine_phone_colname(df)
    phone_col_msg = 'Phone column: {}'.format(phonecol)
    logging.info(phone_col_msg)

    df[phonecol] = df[phonecol].astype(str)

    phones = get_unique_phones_list(df)
    number_of_unique_numbers_msg = 'Number of unique phone numbers to process: {}'.format(len(phones))
    logging.info(number_of_unique_numbers_msg)

    logging.info('Beginning RPV testing...')
    df_result = get_RPV_results_df(phones, check_archive)
    logging.info('RPV results gathered! Joining results to inputs.')

    # join RPV results to df
    final_res = pd.merge(left=df,
                         right=df_result,
                         left_on=phonecol,
                         right_on='phone',
                         how='left')[final_cols]    # could potentially cause an error if any columns in original df
                                                    # have identical names to RPV result fields, 'status'...'carrier'
                                                    # because columns with duplicate names are renamed on join.

    # calculate how many records came back as each status
    report = {}
    rpv_statuses = [
        'connected',
        'connected-75',
        'pending',
        'disconnected',
        'disconnected-85',
        'disconnected-70',
        'disconnected-50',
        'busy',
        'unreachable',
        'invalid',
        'restricted',
        'ERROR',
        'unauthorized',
        'invalid-format',
        'invalid-phone',
        'bad-zip-code',
        'server-unavailable'
    ]
    for status in rpv_statuses:
        report[status] = len(final_res[final_res['status'].apply(lambda x: status == x)])
    logging.info('RPV status count report:')
    logging.info(pformat(report))

    """ ----- EXPORTING RESULTS ----- """
    date = datetime.datetime.now().date()  # used for time-stamping
    outfile_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\RPV\\output\\'
    outfile_path = outfile_dir + 'RPV_results_' + str(date) + '.csv'

    outfile_msg = 'Creating output file at {}'.format(outfile_path)
    logging.info(outfile_msg)
    final_res.to_csv(outfile_path, index=False)

    """ ----- CREATING BATCH DELETE FILE ----- """
    # Only proceed with creating batch delete file if explicitly stated
    if batch_del:
        logging.info('Making batch delete file.')
        # Creating Batch Delete for "disconnected" results

        df_dc = final_res[final_res['status'] == 'disconnected'][phonecol]  # series
        df_dc = pd.DataFrame(df_dc)

        # get all MEs from PPD with one of these disconnected phone numbers
        ppd = get_ppd.get_ppd()
        df_me_phone = ppd[['ME', 'TELEPHONE_NUMBER']]
        df_me_phone = df_me_phone[df_me_phone['TELEPHONE_NUMBER'].notna()]
        df_me_phone.columns = ['me', 'phone']  # batch load file requires these column names

        # create list of me-phone pairs for disconnected numbers
        deletes = pd.merge(left=df_me_phone,
                           right=df_dc,
                           left_on='phone',
                           right_on=phonecol,
                           how='inner')[['me', 'phone']]

        # filling out necessary columns for batch delete file
        deletes['fax'] = ''
        deletes['source'] = ''
        deletes['verified_date'] = ''
        deletes['load_type'] = 'D'  # column changed from 'delete' 'Y' to 'load_type' 'A'append 'R'replace 'D'delete

        deletes = deletes.drop_duplicates()

        batch_del_filename = 'HSG_PHYS_DELETES_RPV_{}.csv'.format(date)
        batch_del_dir = 'U:\\Source Files\\Data Analytics\\BatchLoads\\'
        batch_del_file_path = batch_del_dir + batch_del_filename

        # Write batch delete file
        deletes.to_csv(batch_del_file_path, index=False)

    return final_res
