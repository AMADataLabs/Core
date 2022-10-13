from datetime import date
import pandas as pd
import settings
import os
import json
from datalabs.access.edw import EDW, PartyKeyType
from fuzzywuzzy import fuzz
import logging
import useful_functions as use
import create_load_file as load

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def clean_older_polos():
    older_polos = pd.read_csv('../../Data/POLO_Filter/Older_Filtered_POLOs_2021-08-26.csv', low_memory=False)
    older_polos['ME'] = use.fix_me(older_polos.ME)
    older_polos['IQVIA_ME'] = [x[0:10] for x in older_polos.ME]

def clean(dataframe, older_polos, phone, type):
    dataframe = dataframe.fillna('None')
    dataframe['ME'] = use.fix_me(dataframe.ME)
    dataframe = dataframe[dataframe.ME.isin(older_polos.ME)]
    dataframe[f'{type}_PHONE'] = [use.fix_phone(x) if x !='None' else x for x in dataframe[phone]]
    return dataframe

def clean_dhc():
    dhc = load.get_newest('DHC_FOLDER','DHC')
    dhc = dhc.rename(columns={
        'Zip_Code':'ZIP_DHC',
        'State':'STATE_DHC',
        'City':'CITY_DHC',
        'Address': 'ADDRESS_1_DHC',
        'Address1': 'ADDRESS_2_DHC'
    })
    dhc = dhc.fillna('None')
    dhc['ME'] = use.fix_me(dhc.ME)
    dhc = dhc[dhc.ME.isin(older_polos.ME)]
    dhc['DHC_PHONE'] = [use.fix_phone(x) for x in dhc['Phone_Number']]

def clean_datagov():
    gov = load.get_newest('DATAGOV_FOLDER','All_Data')
    gov = gov.fillna('None')
    gov['ME'] = use.fix_me(gov.ME)
    gov = gov[gov.ME.isin(older_polos.ME)]
    gov['GOV_PHONE'] = [use.fix_phone(x) if x !='None' else x for x in gov['phone']]
    gov = gov.rename(columns={
        'zip':'ZIP_GOV',
        'st':'STATE_GOV',
        'cty':'CITY_GOV',
        'adr_ln_2': 'ADDRESS_2_GOV',
        'adr_ln_1': 'ADDRESS_1_GOV'
    })

def clean_iqvia():
    iqvia =iqvia.fillna('None')
    iqvia = iqvia[iqvia.ME.isin(older_polos.IQVIA_ME)]
    iqvia['IQVIA_PHONE'] = [use.fix_phone(x) if x !='None' else x for x in iqvia['PHONE']]
    iqvia = iqvia.rename(columns={
        'PHYSICAL_ZIP':'ZIP_IQVIA',
        'PHYSICAL_STATE':'STATE_IQVIA',
        'PHYSICAL_CITY':'CITY_IQVIA',
        'PHYSICAL_ADDR_1': 'ADDRESS_1_IQVIA',
        'PHYSICAL_ADDR_2': 'ADDRESS_2_IQVIA'
    })

def clean_symphony():
    symphony =symphony.fillna('None')
    symphony= symphony[symphony.SYM_ME.isin(older_polos.IQVIA_ME)]
    symphony['SYM_PHONE'] = [use.fix_phone(x) for x in symphony['TELEPHONE']]
    symphony = symphony.rename(columns={
        'ZIP':'ZIP_SYMPHONY',
        'STATE':'STATE_SYMPHONY',
        'CITY':'CITY_SYMPHONY',
        'MAILING_LINE_1': 'ADDRESS_2_SYMPHONY',
        'MAILING_LINE_2': 'ADDRESS_1_SYMPHONY'
    })