import settings
import pandas as pd
import usaddress
import pyodbc
from fuzzywuzzy import fuzz
import useful_functions as use
import os
import logging
import datalabs.access.ods

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

#dhc
def clean_input(input_data, source):
    input_data = input_data.fillna('None')
    input_data['ME'] = use.fix_me(input_data.ME)
    input_data[f'{source}_PHONE'] = [use.fix_phone(x) if x !='None' else x for x in input_data['phone']]
    input_data['IQVIA_ME'] = [x[0:10] for x in input_data.ME]
    return input_data

def get_dhc():
    dhc_folder =  os.environ.get('DHC_FOLDER')
    dhc_path = use.get_newest(dhc_folder, 'DHC')
    dhc = pd.read_csv(dhc_path, low_memory=False)
    dhc = dhc.rename(columns={
                            'Zip Code':'ZIP_DHC',
                            'State':'STATE_DHC',
                            'City':'CITY_DHC',
                            'Address': 'ADDRESS_1_DHC',
                            'Address1': 'ADDRESS_2_DHC',
                            'Phone_Number': 'phone'
                        })
    return dhc

#gov
def get_gov():
    gov_folder =  os.environ.get('GOV_FOLDER')
    gov_path = use.get_newest(gov_folder, 'All_Data')
    gov = pd.read_csv(gov_path, low_memory=False)
    gov = gov.rename(columns={
                            'zip':'ZIP_GOV',
                            'st':'STATE_GOV',
                            'city':'CITY_GOV',
                            'adr_ln_2': 'ADDRESS_2_GOV',
                            'adr_ln_1': 'ADDRESS_1_GOV'
                        })
    return gov

#iqvia
def get_iqvia():
    LOGGER.info('Getting IQVia data...')
    with ODS() as ods:
        iqvia = ods.read(os.environ.get('IQVIA_QUERY'))
    iqvia = iqvia.rename(columns={
                                'PHYSICAL_ZIP':'ZIP_IQVIA',
                                'PHYSICAL_STATE':'STATE_IQVIA',
                                'PHYSICAL_CITY':'CITY_IQVIA',
                                'PHYSICAL_ADDR_1': 'ADDRESS_1_IQVIA',
                                'PHYSICAL_ADDR_2': 'ADDRESS_2_IQVIA',
                                'PHONE': 'phone',
                                'ME':'IQVIA_ME'
                    })
    return iqvia

#symphony
def get_symphony():
    LOGGER.info('Getting Symphony data...')
    with ODS() as ods:
        symphony = ods.read(os.environ.get('SYMPHONY_QUERY'))
    symphony = symphony.rename(columns={
                                        'ZIP':'ZIP_SYMPHONY',
                                        'STATE':'STATE_SYMPHONY',
                                        'CITY':'CITY_SYMPHONY',
                                        'MAILING_LINE_1': 'ADDRESS_2_SYMPHONY',
                                        'MAILING_LINE_2': 'ADDRESS_1_SYMPHONY',
                                        'TELEPHONE':'phone',
                                        'SYM_ME':'IQVIA_ME'
                                    })
    return symphony

def universalize_columns(df, source):
    df['ADDRESS_1'] = df[f'ADDRESS_1_{source}']
    df['ADDRESS_2'] = df[f'ADDRESS_2_{source}']
    df['CITY'] = df[f'CITY_{source}']
    df['STATE'] = df[f'STATE_{source}']
    df['ZIPCODE'] = df[f'ZIP_{source}']
    df['PHONE'] = df[f'{source}_PHONE']
    numb_list = list(range(0,len(df)))
    df['KEY'] = [str(s) + source for s in numb_list]
    return df

def clean_address_two(add_1):
    add_1 = add_1.strip()
    if add_1 == 'None':
        addr_1 = ' '
    elif add_1 == 'NAN':
        addr_1 = ' '
    else:
        addr_1 = ',' + add_1
    return addr_1

def error_handle(parsed_string):
    new_dict = {}
    for thing in parsed_string:
        if thing[1] in new_dict.keys():
            a_list = [new_dict[thing[1]], thing[0]]
            new_dict[thing[1]] = max(a_list, key=len)
        else:
            new_dict[thing[1]] = thing[0]
    return new_dict

def fix(component):
    component = component.strip().upper()
    return component

def fix_zipcode(num):
    num = str(num).strip().replace('.0', '')
    num = ''.join(filter(str.isdigit, num))
    if len(num) > 5:
        num = num[:-4]
    if len(num) == 4:
        num = '0' + num
    elif len(num) == 3:
        num = '00' + num
    elif len(num) == 2:
        num = '000' + num
    return num

def parse_address(moar, source):
    dict_list = []
    mes = []
    for row in moar.itertuples():
        addr_2 = clean_address_two(row.ADDRESS_2)
        address = f'{fix(row.ADDRESS_1)}{addr_2}, {fix(row.CITY)}, {fix(row.STATE)}'
        try:
            address_dict = usaddress.tag(address)[0]
        except usaddress.RepeatedLabelError as e:
            print(e.original_string)
            address_dict = error_handle(e.parsed_string)
            print('')
        address_dict['KEY'] = row.KEY
        address_dict['PHONE'] = row.PHONE
        address_dict['ZIPCODE'] = row.ZIPCODE
        address_dict['ZIP'] = fix_zipcode(row.ZIPCODE)
        dict_list.append(address_dict)
        mes.append(row.IQVIA_ME)
    parsed_df = pd.DataFrame(dict_list)
    parsed_df.dropna(how='all', axis=1, inplace=True)
    parsed_df.columns = [f'{c}_{source}' for c in parsed_df.columns.values]
    parsed_df['IQVIA_ME'] = mes
    return parsed_df

def merge_data(source_list):
    for source_dict in source_list:
        universalize_columns(source_dict['DATA'], source_dict['SOURCE'])
        source_dict['PARSED_DATA'] = parse_address(source_dict['DATA'], source_dict['SOURCE'])
    all_the_data = source_list[0]['PARSED_DATA'].merge(source_list[1]['PARSED_DATA'],on='IQVIA_ME',how='outer').merge(source_list[2]['PARSED_DATA'],on='IQVIA_ME',how='outer').merge(source_list[3]['PARSED_DATA'],on='IQVIA_ME',how='outer')
    all_the_data['ROW_KEY'] = list(range(0,len(all_the_data)))
    all_the_data = all_the_data.fillna('None')
    return all_the_data

def is_a_match(thing_1, thing_2):
    if thing_1 == thing_2:
        match = True
    elif thing_1 in thing_2:
        match = True
    elif thing_2 in thing_1:
        match = True
    elif fuzz.ratio(thing_1, thing_2)>75:
        match = True
    else:
        match = False
    return match

def find_phone_matches(all_the_data):

def find_address_matches(all_the_data):




def find_new_data():
    source_list = [
    {'SOURCE':'DHC',
    'DATA':dhc},
    {'SOURCE':'IQVIA',
    'DATA':iqvia},
    {'SOURCE':'SYMPHONY',
    'DATA':symphony},
    {'SOURCE':'GOV',
    'DATA':gov}
    ]