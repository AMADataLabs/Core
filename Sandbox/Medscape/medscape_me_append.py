'''
This script scrapes the Medscape In Memorium feature
'''
from datetime import datetime
import pandas as pd
from nameparser import HumanName
from medscape_scrape import scrape

#Set today
TODAY = str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '')

#Set Output Directory
OUT_DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Medscape/'

#Define ppd
PPD_FILE = 'U:/Source Files/Data Analytics/Data-Science/Data/PPD/ppd_data_20200404.csv'
print('Reading PPD...')
PPD = pd.read_csv(PPD_FILE)

print('Scraping...')
DICT_LIST = scrape()
ALL_DATA = pd.DataFrame(DICT_LIST)
USA_DATA = ALL_DATA[ALL_DATA.COUNTRY == 'USA']
ALL_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_Scrape_{TODAY}.csv', index=False)
USA_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_Scrape_USA_{TODAY}.csv', index=False)

def split_names(roster_df):
    '''Splits name column into components'''
    roster_df = roster_df.drop_duplicates()
    dict_list = []
    for row in roster_df.itertuples():
        name_parsed = HumanName(row.NAME)
        name_dict = {
            'NAME':row.NAME,
            'FIRST_NAME': name_parsed.first.upper(),
            'LAST_NAME': name_parsed.last.upper(),
            'MIDDLE_NAME': name_parsed.middle.upper(),
            'SUFFIX':name_parsed.suffix.upper(),
            'NICKNAME':name_parsed.nickname.upper(),
            'TITLE':name_parsed.title.upper(),
        }
        dict_list.append(name_dict)
    name_df = pd.DataFrame(dict_list)
    new_df = pd.merge(name_df, roster_df, on='NAME')
    return new_df

def append_me(roster_df):
    '''Matches to PPD and appends ME'''
    data_split = split_names(roster_df)

    bad_spec_words = [
        'Nurse',
        'Vet',
        'Transport',
        'Assistant',
        'Receptionist'
    ]

    mes = []
    for row in data_split.itertuples():
        physician_me = 'None'
        keep = True
        for word in bad_spec_words:
            if word in row.SPECIALTY:
                keep = False
        if keep:
            new_df = PPD[(PPD.FIRST_NAME == row.FIRST_NAME)&(PPD.LAST_NAME == row.LAST_NAME)]
            if len(new_df) == 0:
                pass
            elif len(new_df) > 1:
                new_df = new_df[new_df.BIRTH_YEAR.isin([2019.0-int(row.AGE), 2020.0-int(row.AGE)])]
                if len(new_df) > 1:
                    print('wtf')
            if len(new_df) == 1:
                physician_me = list(new_df.ME)[0]
        mes.append(physician_me)

    data_split['ME'] = mes
    data_me = data_split[data_split.ME != 'None']
    return data_me

print('Matching and appending ME numbers...')
USA_DATA_ME = append_me(USA_DATA)
USA_DATA_ME.to_csv(f'{OUT_DIRECTORY}Memorium_Scrape_USA_Physicians_{TODAY}.csv', index=False)
