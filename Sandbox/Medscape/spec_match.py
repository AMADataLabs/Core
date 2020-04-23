'''
This script confirms matched specialties of matched physiciains
'''
import os
from fuzzywuzzy import fuzz
import pandas as pd
import settings

def get_spec_table():
    '''Get specialty conversion table'''
    spec_file = os.environ.get('SPEC_FILE')
    spec_table = pd.read_csv(spec_file)
    return spec_table

def match_spec(ppd_df, specialty, spec_table):
    '''Checks fuzzy matching on specialty'''
    mf_spec_cd = ppd_df.iloc[0]['PRIM_SPEC_CD']
    specialty = specialty.title()
    mf_spec = spec_table[spec_table.SPEC_CD == mf_spec_cd].iloc[0]['DESC'].title()
    specialty = specialty.replace('Primary Care', 'Family Medicine')
    specialty = specialty.replace('OB-GYN', 'Obstetrics & Gynecology')
    specialty = specialty.replace('Ob/Gyn', 'Obstetrics & Gynecology')
    specialty = specialty.replace('trist', 'try').replace('gist', 'gy')
    specialty = specialty.replace('eon', 'ery').replace('cian', 's')
    if mf_spec in specialty:
        return True
    elif fuzz.ratio(mf_spec, specialty) > 40:
        return True
    elif mf_spec == 'Unspecified' and 'Resident' in specialty:
        return True
    elif mf_spec == 'Unspecified':
        return True
    else:
        return False
