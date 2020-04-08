'''
This script scrapes the Medscape In Memorium feature and appends ME numbers to US Physicians
'''
from datetime import date
import pandas as pd
from nameparser import HumanName
#from medscape_scrape import scrape
from datetime import datetime
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests

#Set today
TODAY = str(date.today())

#Set Output Directory
OUT_DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Medscape/'

#Define ppd
PPD_FILE = 'U:/Source Files/Data Analytics/Data-Science/Data/PPD/ppd_data_20200404.csv'
print('Reading PPD...')
PPD = pd.read_csv(PPD_FILE)

def scrape():
    '''Scrapes the medscape in memorium page'''
    med_url = 'https://www.medscape.com/viewarticle/927976#vp_1'
    response = requests.get(med_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_text = soup.text

    with open(f'{OUT_DIRECTORY}Memorium_Text_{TODAY}.txt', 'w') as outfile:
        json.dump(all_text, outfile)

    all_pars = soup.find_all('p')

    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
              "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
              "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
              "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
              "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
              "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
              "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
              "Puerto Rico","Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

    dict_list = []
    for paragraph in all_pars[6:-10]:
        name = 'None'
        age = 'None'
        specialty = 'None'
        city = 'None'
        state = 'None'
        country = 'None'
        location = 'None'
        try:
            info_text = paragraph.text.replace('\n', '').replace('\xa0', '')
            info_list = info_text.split(', ')
            info_update = []
            for info in info_list:
                info_update += (info.split(','))
            info_list = info_update
            name = info_list[0]
            if len(info_list) == 4:
                age = info_list[1]
                specialty = info_list[2]
                city = info_list[3]
            else:
                for info in info_list:
                    info = info.replace(' (presumed)', '')
                    if info.isnumeric() or info == 'age unknown':
                        age = info
                    if info in states:
                        state = info
                        country = 'USA'
                        city = info_list[-2]
                if country != 'USA':
                    country = info_list[-1].replace(' (presumed)', '')
                    city = info_list[-2]
                if age != 'None':
                    remain = info_text.split(f'{age},')[1]
                    remainder = remain.replace(f'{city}, ', '').replace(state, '')
                    remainder = remainder.replace(country, '')
                    if remainder[0] == ' ':
                        remainder = remainder[1:]
                    specialty = remainder.replace(', ', '  ')
                    remainder_list = remainder.split(', ')
                    if len(remainder_list) > 2:
                        location = remainder_list[-2]
                        specialty = remainder.replace(location, '').replace(', ', ' ')
            specialty = specialty.replace('  ', '')
            if len(specialty) > 1:
                if specialty[-1] == ' ':
                    specialty = specialty[:-1]
            if country == 'New York City':
                city = 'New York City'
            if city == 'New York City':
                country = 'USA'
                state = 'New York'
            if city == 'Washington':
                state = 'DC'
                specialty = specialty.replace(',DC', '')
            if city == 'age unknown':
                city = 'None'
            if country == 'None':
                country = city
                city = 'None'
        except IndexError as index_error:
            print('Human intervention needed for the following exception:')
            print(index_error)
            print(paragraph.text)
            print(' ')
        new_dict = {
            'NAME': name,
            'AGE': age,
            'SPECIALTY': specialty,
            'CITY': city,
            'STATE': state,
            'COUNTRY': country,
            'LOCATION': location
        }
        dict_list.append(new_dict)
    return dict_list

print('Scraping...')
DICT_LIST = scrape()
ALL_DATA = pd.DataFrame(DICT_LIST)
USA_DATA = ALL_DATA[ALL_DATA.COUNTRY == 'USA']
ALL_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_{TODAY}.csv', index=False)
USA_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_USA_{TODAY}.csv', index=False)

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
    return data_split, data_me

print('Matching and appending ME numbers...')
USA_DATA_SPLIT, USA_DATA_ME = append_me(USA_DATA)
USA_DATA_ME.to_csv(f'{OUT_DIRECTORY}Memorium_USA_Physicians_{TODAY}.csv', index=False)
USA_DATA_SPLIT.to_csv(f'{OUT_DIRECTORY}Memorium_USA_ME_{TODAY}.csv', index=False)
