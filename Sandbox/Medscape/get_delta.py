'''
This script compiles some statistics about medscape data
'''
import os
from datetime import date, timedelta
import pandas as pd

TODAY = str(date.today())
YESTERDAY = str(date.today() - timedelta(days=1))

DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Medscape/'

def newest(path, text):
    '''Grabs newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

US_YESTERDAY = newest(DIRECTORY, f'USA_ME_{YESTERDAY}')
US_TODAY = newest(DIRECTORY, f'USA_ME_{TODAY}')
ALL_YESTERDAY = newest(DIRECTORY, f'Memorium_{YESTERDAY}')
ALL_TODAY = newest(DIRECTORY, f'Memorium_{TODAY}')

US_DATA_TODAY = pd.read_csv(US_TODAY)
US_DATA_YESTERDAY = pd.read_csv(US_YESTERDAY)
ALL_DATA_TODAY = pd.read_csv(ALL_TODAY)
ALL_DATA_YESTERDAY = pd.read_csv(ALL_YESTERDAY)

INTERSECT_US = list(pd.merge(US_DATA_TODAY, US_DATA_YESTERDAY, on=['NAME',
                                                                   'AGE',
                                                                   'SPECIALTY',
                                                                   'LOCATION',
                                                                   'CITY',
                                                                   'STATE',
                                                                   'COUNTRY'
                                                                   ])['NAME'])
US_DELTA = US_DATA_TODAY[US_DATA_TODAY.NAME.isin(INTERSECT_US) == False]

INTERSECT_ALL = list(pd.merge(ALL_DATA_TODAY, ALL_DATA_YESTERDAY, on=['NAME',
                                                                      'AGE',
                                                                      'SPECIALTY',
                                                                      'LOCATION',
                                                                      'CITY',
                                                                      'STATE',
                                                                      'COUNTRY'
                                                                      ])['NAME'])
ALL_DELTA = ALL_DATA_TODAY[ALL_DATA_TODAY.NAME.isin(INTERSECT_ALL) == False]

US_DELTA.to_csv(f'{DIRECTORY}Memorium_USA_Delta_{TODAY}.csv', index=False)
ALL_DELTA.to_csv(f'{DIRECTORY}Memorium_World_Delta_{TODAY}.csv', index=False)
