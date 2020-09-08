

import pyodbc
import string

import pandas as pd
import numpy as np

from datetime import datetime
import os

import sys
""" This line allows for the import below """
sys.path.insert(0, 'U:\\Source Files\\Data Analytics\\Data-Science\\Code-Library\\Common_Code\\')
from outlook import send_email
from pyxcel import format_and_save


# read the flag word Excel file
flags_df = pd.read_excel('U:\\Source Files\\Data Analytics\\Data-Science\\Code-Library\\' +
                         'AMC_Address_Sweep\\AMC_flag_words.xlsx',
                         header=0)
# convert the excel file dataframe to a list
flag_words = [str(r['FLAG_WORDS']).lower() for i, r in flags_df.iterrows()]

false_positives = [
        'sebastopol',
        'mail stop',
        'mail code',
        'mailstop',
        'mail center',
        'mail slot',
        'mailslot',
        'mail ctr',
        'vanderbilt mail'
]


def is_flagged_city(city_string):
    city_string = city_string.lower()
    return any([city_string == '',
                len(set(city_string)) == 1,
                any([d in city_string for d in string.digits])
                ])


def is_flagged_addr1(addr1_string):
    if addr1_string is None:
        return True

    addr1_string = addr1_string.lower()
    return any([addr1_string == '',
                len(set(addr1_string)) <= 2,
                addr1_string.isdigit(),

                ])


def is_flagged_state(state_string):
    state_string = state_string.lower()
    return any([state_string == '',
                len(state_string) != 2,
                len(set(state_string)) != 2,
                any([c not in string.ascii_letters for c in state_string])
                ])


def is_flagged_zip(zip_string):
    zip_string = zip_string.lower()

    return any([any([c not in string.digits for c in zip_string]),
                len(zip_string) > 5
                ])


# checks the aggregated address string for flag words
def contains_flagword(addr_string, false_positives=[]):
    addr_string = addr_string.lower()

    # we want to avoid false positive markers from flagging the method that checks for flag words.
    # this is done by removing the text of false positives from the aggregated address text before
    # we search that text for flag words.
    for fp in false_positives:
        if fp in addr_string:
            # print('fp')
            addr_string = addr_string.replace(fp, '')

    tokens = addr_string.split()

    return any([t in flag_words for t in tokens])


def get_clean_AMC_data(aims_conn):

    # Query for the active AIMS data
    query = \
        """
        SELECT 
            eke.key_type_val as ME, 
            ecu.entity_id,
            ecu.comm_id,
            first_nm,
            middle_nm,
            last_nm,
            pa.addr_line0, 
            pa.addr_line1, 
            pa.addr_line2, 
            pa.city_cd, 
            pa.zip,
            pa.state_cd,
            ecu.usg_begin_dt,
            ecu.comm_usage

        FROM 
            entity_comm_usg_at ecu

            INNER JOIN

            entity_key_et eke
            ON eke.entity_id = ecu.entity_id

            INNER JOIN

            post_addr_at pa
            ON pa.comm_id = ecu.comm_id

            INNER JOIN 

            person_name_et pn
            ON pn.entity_id = ecu.entity_id

        WHERE 
            ecu.comm_usage = 'amc' AND
            ecu.end_dt is null     AND
            pn.name_type ='LN'     AND
            pn.end_dt is null      AND
            eke.key_type ='ME'
        """

    # Execute the query (takes about 3-5 minutes)
    print('Querying AIMS for active amc data.')
    df = pd.read_sql(query, aims_conn, coerce_float=False)
    print('Query complete. Cleaning data.')

    # replacements must be made because the read_sql results come back with
    # the whitespace to fill the field size from the original table
    df = df.replace(np.nan, '', regex=True)
    # strip all whitespace
    for col in df:
        df[col] = df[col].astype(str).apply(lambda x: x.strip())

    # putting together all address fields into a single column.
    # this address column is where I'll be searching for flag words

    df['address'] = df['addr_line0'].str.lower() + ' ' + \
                    df['addr_line1'].str.lower() + ' ' + \
                    df['addr_line2'].str.lower() + ' ' + \
                    df['city_cd'].str.lower() + ' ' + \
                    df['state_cd'].str.lower()

    # attempts to mitigate wonky date formatting (some rows have this date as a string with brackets. wtf.
    df['usg_begin_dt'] = df['usg_begin_dt'].apply(lambda x: x.replace('[', '').replace(']', ''))
    df['usg_begin_dt'] = df['usg_begin_dt'].apply(lambda x: x[:x.index(':')] if ':' in x else x)

    # need to simplify usg_begin_dt format to make Excel report easier to read.
    # currently read as a string. convert to datetime then take date.
    df['usg_begin_dt'] = pd.to_datetime(df['usg_begin_dt']).apply(datetime.date)

    print('Done cleaning data.')
    return df


def get_flagged_AMC_data(df, check_line1=False):
    results_summary = ''

    # putting together all address fields into a single column.
    # this address column is where I'll be searching for flag words

    df['address'] = df['addr_line0'].str.lower() + ' ' + \
                    df['addr_line1'].str.lower() + ' ' + \
                    df['addr_line2'].str.lower() + ' ' + \
                    df['city_cd'].str.lower() + ' ' + \
                    df['state_cd'].str.lower()

    # check Address Line 1
    if check_line1:
        df['addr1_flagged'] = df['addr_line1'].apply(lambda x: is_flagged_addr1(x))
    else:
        if 'addr1_flagged' in df.columns:
            del df['addr1_flagged']

    # Apply each check function
    df['city_flagged'] = df['city_cd'].apply(lambda x: is_flagged_city(x))
    df['state_flagged'] = df['state_cd'].apply(lambda x: is_flagged_state(x))
    df['zip_flagged'] = df['zip'].apply(lambda x: is_flagged_zip(x))
    df['contains_flag_word'] = df['address'].apply(lambda x: contains_flagword(x, false_positives))

    # Keep track of counts of each
    n_c = len(df[df['city_flagged']])
    n_s = len(df[df['state_flagged']])
    n_z = len(df[df['zip_flagged']])
    n_f = len(df[df['contains_flag_word']])

    flags = {
        'city': n_c,
        'state': n_s,
        'zip': n_z,
        'flag_word': n_f
    }

    # Make a list to mark if any of the check columns are True, each row is 1 element in the list
    if check_line1:
        df['addr1_flagged'] = df['addr_line1'].apply(lambda x: is_flagged_addr1(x))

        n_a = len(df[df['addr1_flagged']])
        flags['addr1'] = n_a

        any_flags = []
        for i, row in df.iterrows():
            # state = row['state_cd']
            # zipcode = row['zip']
            # mismatch = zip_state_mismatch(zipcode, state)
            # zip_state_mismatches.append(mismatch)
            a = any([row['addr1_flagged'],
                     row['city_flagged'],
                     row['state_flagged'],
                     row['zip_flagged'],
                     row['contains_flag_word']
                     ])
            any_flags.append(a)
    else:
        any_flags = []
        for i, row in df.iterrows():
            # state = row['state_cd']
            # zipcode = row['zip']
            # mismatch = zip_state_mismatch(zipcode, state)
            # zip_state_mismatches.append(mismatch)

            a = any([row['city_flagged'],
                     row['state_flagged'],
                     row['zip_flagged'],
                     row['contains_flag_word']
                     ])
            any_flags.append(a)

    # Make the column from any_flags
    df['any_flag'] = any_flags

    results_summary += 'Count of all flagged amc-sourced addresses: {}'.format(len(df[df['any_flag']]))
    results_summary += '\nSpecific breakdown: (addresses can be flagged by multiple fields, ' \
                       'so the sum of these could exceed count above)'
    for f in flags:
        val = flags[f]
        if val > 0:
            results_summary += '\n\t{}: {}'.format(f, val)

    df.drop(columns='address', axis=1, inplace=True)  # delete temp column
    df.drop_duplicates(inplace=True)

    # Returns only rows with any flagged address fields
    return df[df['any_flag'] == True], results_summary


# Writes a DataFrame to an Excel Workbook
def write_output_to_excel(df,
                          output_path='output.xlsx',
                          sheetname='Sheet1',
                          password=None):
    # reference:
    # https://xlsxwriter.readthedocs.io/example_pandas_header_format.html

    # isolate the the folder path from the full file path
    if '\\' in output_path:
        output_dir = output_path[:output_path.rfind('\\')]

        # if the directory does not exist, make it.
        if output_dir != '' and not os.path.exists(output_dir):
            os.mkdir(output_dir)

    print('Path', output_path)

    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

    df.to_excel(writer, sheet_name=sheetname, startrow=1, header=False, index=False)

    my_workbook = writer.book
    worksheet = writer.sheets[sheetname]

    # define header format
    header_format = my_workbook.add_format(
        {
            'bold': True,
            'align': 'center',
            'valign': 'center',
        }
    )

    worksheet.freeze_panes(1, 0)  # freeze top row

    # write columns to the first row.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)

    writer.save()

    # with the data written, we just format it and save with win32com.
    format_and_save(output_path, password)

    return


if __name__ == '__main__':

    date = str(datetime.now().date())

    # Reads Windows Environment variable 'auth_aims' which is a string with the
    # username and password separated by a space.
    auth_aims = os.getenv('auth_aims').split()
    username = auth_aims[0]
    password = auth_aims[1]

    # Establish AIMS Connection
    aims_conn = pyodbc.connect("DSN=aims_prod; UID={}; PWD={}".format(username, password))
    aims_conn.execute("SET ISOLATION TO DIRTY READ;")

    df = get_clean_AMC_data(aims_conn)

    flagged_df, results_summary = get_flagged_AMC_data(df, check_line1=False)
    flagged_df['date_checked'] = date

    # TODO: Edit Path to U drive project directory
    output_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\AMC_Address_Sweep\\output\\'

    archive_dir = output_dir + '_archive\\'
    output_file_path = output_dir + 'AMC_flagged_address_records_' + date + '.csv'

    flagged_df.to_csv(output_file_path, index=False)

    print(results_summary)

    body = \
        """Hello,
    
Attached are the results for today's amc flagging script:
{}
        
This report and email were generated automatically.
If you believe there are errors or if you have questions or suggestions, please reply to let me know.
        
Thanks!    
""".format(results_summary)

    output_file_path = output_file_path.replace('.csv', '.xlsx')

    write_output_to_excel(df=flagged_df,
                          output_path=output_file_path,
                          sheetname='Flagged Records',
                          password='Survey19')

    to = ['Nicole.Neal@ama-assn.org', 'Sandeep.Dhamale@ama-assn.org']
    cc = ['Anthony.Liu@ama-assn.org', 'Debbie.Kidd@ama-assn.org', 'Garrett.Lappe@ama-assn.org']

    # TODO: Edit email with correct recipients and cc
    send_email(to=['Garrett.Lappe@ama-assn.org'],
               cc=[],
               subject='AMC Sweep Results - {}'.format(date),
               body=body,
               attachments=[output_file_path])



