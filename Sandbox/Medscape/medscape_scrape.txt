'''
This script scrapes the Medscape In Memorium feature
'''
from datetime import date
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests

#Set today
TODAY = str(date.today())

#Set Output Directory
OUT_DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Medscape/'
URL = 'https://www.medscape.com/viewarticle/927976#vp_1'
RESPONSE = requests.get(URL)
SOUP = BeautifulSoup(RESPONSE.content, 'html.parser')
ALL_TEXT = SOUP.text

with open(f'{OUT_DIRECTORY}Memorium_Text_{TODAY}.txt', 'w') as outfile:
    json.dump(ALL_TEXT, outfile)

PS = SOUP.find_all('p')

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
          "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
          "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
          "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
          "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
          "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
          "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
          "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

DICT_LIST = []
for paragraph in PS[6:-10]:
    name = 'None'
    age = 'None'
    specialty = 'None'
    city = 'None'
    state = 'None'
    country = 'None'
    location = 'None'
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
            if info.isnumeric() or info == 'age unknown':
                age = info
            if info in STATES:
                state = info
                country = 'USA'
                city = info_list[-2]
        if country != 'USA':
            country = info_list[-1]
            city = info_list[-2]
        if age != 'None':
            remainder = info_text.split(f'{age},')[1]
            remainder = remainder.replace(f'{city}, ', '').replace(state, '').replace(country, '')
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
        country = 'USA'
        city = 'New York City'
        state = 'New York'
    if city == 'Washington':
        state = 'DC'
        specialty = specialty.replace(',DC', '')
    if city == 'age unknown':
        city = 'None'
    new_dict = {
        'NAME': name,
        'AGE': age,
        'SPECIALTY': specialty,
        'CITY': city,
        'STATE': state,
        'COUNTRY': country,
        'LOCATION': location
    }
    DICT_LIST.append(new_dict)

ALL_DATA = pd.DataFrame(DICT_LIST)
USA_DATA = ALL_DATA[ALL_DATA.COUNTRY == 'USA']
ALL_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_Scrape_{TODAY}.csv', index=False)
USA_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_Scrape_USA_{TODAY}.csv', index=False)
