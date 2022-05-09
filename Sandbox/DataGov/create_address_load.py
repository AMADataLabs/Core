import pandas as pd
import get_new_file as load
import settings
import useful_functions as use
from datetime import date
import os
import datacompy
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_delta(new_file, previous_load):
    new_file = new_file.dropna(subset=['ME'])
    new_file.ME = [use.fix_me(x) for x in new_file.ME]
    previous_load['ME'] = [use.fix_me(x) for x in previous_load['me#']]
    compare = datacompy.Compare(new_file, previous_load, join_columns=['ME','adrs_id'], df1_name = 'new', df2_name = 'old')
    delta = compare.df1_unq_rows
    return delta

def get_columns():
    columns = ['entity_id',
                'me#',
                'comm_id',
                'usage',
                'load_type',
                'addr_type',
                'addr_line_1',
                'addr_line_2',
                'addr_line_3',
                'addr_city',
                'addr_state',
                'addr_zip',
                'addr_plus4',
                'addr_country',
                'source',
                'source_dtm',
                'adrs_id'
                ]
    return columns

def clean_file(gov):
    col_rename = {
            'adr_ln_1':'addr_line_1',
            'cty':'addr_city',
            'st':'addr_state',
            'adr_ln_2':'addr_line_2',
            'me':'me#'
        }
    gov = gov.rename(columns=col_rename)
    gov['addr_zip'] = [use.fix_zipcode(x) for x in gov.zip]
    gov['addr_plus4'] = [x if len(str(x))==9 else '' for x in gov.zip]
    gov['load_type'] = 'A'
    gov['addr_type'] = 'OF'
    gov['source'] = 'NAT-DOWN'
    gov['entity_id'] = ''
    gov['comm_id'] = ''
    gov['usage'] = ''
    gov['addr_country'] = ''
    gov['addr_line_3'] = ''
    print(gov.columns)
    gov = gov.drop_duplicates(['me#','adrs_id'])
    return (gov)

def create_address_load():
    today = str(date.today())
    local_folder = os.environ.get('OUT_DIR')
    udrive = os.environ.get('UDRIVE')
    LOGGER.info('Getting new file...')
    new_filename = load.get_datagov()
    LOGGER.info(f'{new_filename}')
    new_file = pd.read_csv(new_filename, low_memory=False)
    LOGGER.info('Getting previous load...')
    previous_load_file = load.get_newest(load.Path.DATAGOV.value,'address_load_national_downloadable_with_id')
    LOGGER.info(f'{previous_load_file}')
    previous_load = pd.read_csv(previous_load_file)
    LOGGER.info('Getting delta...')
    delta = get_delta(new_file, previous_load)
    LOGGER.info(f'{len(delta)} new records found')
    LOGGER.info('Creating file...')
    delta = clean_file(delta)
    delta['source_dtm'] = today
    cols = get_columns()
    with_ids = delta[cols]
    address_load = with_ids.drop(columns=['adrs_id'])
    LOGGER.info('Saving locally...')
    with_ids.to_csv(f'{local_folder}/address_load_national_downloadable_with_id_{today}.csv', index=False)
    address_load.to_csv(f'{local_folder}/address_load_national_downloadable_{today}.csv', index=False)
    # LOGGER.info('Saving to UDrive...')
    # address_load.to_csv(f'{udrive}/address_load_national_downloadable_{today}.csv', index=False)

if __name__ == "__main__":
    create_address_load()