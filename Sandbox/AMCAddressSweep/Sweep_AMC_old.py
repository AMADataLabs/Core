# AMC Address Sweep
# Garrett Lappe - September 2019
#
# Queries addresses sourced from AMC and flags records which are suspected of being invalid / inappropriate.
# Results are exported to CSV for manual review.

import pyodbc
import string
import numpy as np
import pandas as pd
from datetime import datetime


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


def contains_flagword(addr_string):

    false_positives = [
        'sebastopol',
        'mail stop',
        'mail code',
        'mailstop',
        'mail center',
        'mail slot',
        'mailslot',
        'mail ctr'
    ]  # valid address elements which would otherwise trigger a flag for containing the word "mail" or "stop"

    addr_string = addr_string.lower()
    for fp in false_positives:
        if fp in addr_string:
            # print('fp')
            addr_string = addr_string.replace(fp, '')

    tokens = addr_string.split()

    return any([t in flag_words for t in tokens])

    # return any([f in addr_str for f in flag_words])


# def zip_state_mismatch(zip_string, state_string):
#
#    state_string = state_string.lower()
#
#    zipcode = search.by_zipcode(zip_string)
#
#    if zipcode.zipcode is not None:
#        zip_state = zipcode.state.lower()
#        return zip_state != state_string  # return True if there is NOT a match
#
#    return True


def sweep(df, check_line1=False):
    # putting together all address fields into a single column.
    # this address column is where I'll be searching for flag words

    df['address'] = df['addr_line0'].str.lower() + ' ' + \
                    df['addr_line1'].str.lower() + ' ' + \
                    df['addr_line2'].str.lower() + ' ' + \
                    df['city_cd'].str.lower() + ' ' + \
                    df['state_cd'].str.lower()

    if check_line1:
        df['addr1_flagged'] = df['addr_line1'].apply(lambda x: is_flagged_addr1(x))
    else:
        if 'addr1_flagged' in df.columns:
            del df['addr1_flagged']
    df['city_flagged'] = df['city_cd'].apply(lambda x: is_flagged_city(x))
    df['state_flagged'] = df['state_cd'].apply(lambda x: is_flagged_state(x))
    df['zip_flagged'] = df['zip'].apply(lambda x: is_flagged_zip(x))
    df['contains_flag_word'] = df['address'].apply(lambda x: contains_flagword(x))

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

    # zip_state_mismatches = []

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

    df['any_flag'] = any_flags

    print('Count of all flagged addresses: {}'.format(len(df[df['any_flag']])))
    print(
        'Specific breakdown: (addresses can be flagged by multiple fields, so the sum of these could exceed count above)')
    for f in flags:
        val = flags[f]
        if val > 0:
            print('# of addresses with flagged {}: {}'.format(f, val))

    # df['zip_state_mismatch'] = zip_state_mismatches

    df.drop(columns='address', axis=1, inplace=True)
    df['date_checked'] = date

    return df[df['any_flag']]  # all rows with any flag on any address field.


if __name__ == '__main__':

    # aims auth info
    username = ''
    password = ''

    print('Starting Address Sweep...')
    print('Connecting to AIMS')
    AIMS_conn = pyodbc.connect(f"DSN=aims_prod; UID={username}; PWD={password}")
    AIMS_conn.execute("SET ISOLATION TO DIRTY READ;")
    sql3 = \
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
            ecu.usg_begin_dt

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
            ecu.comm_usage = 'AMC' AND
            ecu.end_dt is null     AND
            pn.name_type ='LN'     AND
            pn.end_dt is null      AND
            eke.key_type ='ME'
        """

    print('Querying data...(takes a while)...')
    df = pd.read_sql(sql3, AIMS_conn, coerce_float=False)
    print('Query complete. Cleaning results...')
    # cleaning whitespace
    df = df.replace(np.nan, '', regex=True)
    for col in df:
        df[col] = df[col].astype(str).apply(lambda x: x.strip())
    print('Pre-processing complete. Beginning analysis...')

    print('Number of active AMC records:', len(df))

    flagword_file_path = 'U:\\Source Files\\Data Analytics\\Data-Science' \
                         '\\Code-Library\\AMC_Address_Sweep\\AMC_flag_words.xlsx'

    # read the flag word Excel file
    flags_df = pd.read_excel(flagword_file_path, header=0)
    flag_words = [str(r['FLAG_WORDS']).lower() for i, r in flags_df.iterrows()]

    date = str(datetime.now().date())  # timestamp for the results

    print('Beginning sweep...')
    # Perform the sweep
    output = sweep(df, check_line1=False)
    print('Length output1:', len(output))
    print()
    print('Beginning sweep (null address_line1 = flagged')
    output2 = sweep(df, check_line1=True)
    print('Length output2:', len(output2))

    root = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\AMC_Address_Sweep\\'
    output_dir = root + 'output\\'
    archive_dir = output_dir + '_archive\\'

    filename = output_dir + 'AMC_flagged_address_records_' + date + '.csv'
    filename2 = output_dir + 'AMC_flagged_address_records_inc_line1_' + date + '.csv'

    print('############################ EXPORT RESULTS ############################\n')

    output = output.drop_duplicates()

    print('Writing output of flagged records to: \n\t\'{}\''.format(filename))
    output.to_csv(filename,
                  index=False
                  )
    output.to_csv(archive_dir + 'AMC_sweep_archive.csv', index=False, mode='a+')

    output2 = output2.drop_duplicates()
    print('\nWriting output of flagged records including line1 check to: \n\t\'{}\''.format(filename2))
    output2.to_csv(filename2,
                   index=False
                   )
    output2.to_csv(archive_dir + 'AMC_sweep_w_line1_archive.csv', index=False, mode='a+')

    print('\n############################### FINISHED ###############################')