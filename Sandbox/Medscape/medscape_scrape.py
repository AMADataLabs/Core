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
              "Puerto Rico", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",
              "Wyoming"]

    dict_list = []
    no_link_count = 0
    index = 6
    for paragraph in all_pars[6:-10]:
        if paragraph.text == "\xa0":
            continue
        link = 'None'
        name = 'None'
        age = 'None'
        specialty = 'None'
        city = 'None'
        state = 'None'
        country = 'None'
        location = 'None'
        try:
            link = paragraph.find('a')['href']
        except TypeError:
            no_link_count += 1
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
            print(index)
            print(index_error)
            print(paragraph)
            print(' ')
        new_dict = {
            'NAME': name,
            'AGE': age,
            'SPECIALTY': specialty,
            'CITY': city,
            'STATE': state,
            'COUNTRY': country,
            'LOCATION': location,
            'LINK': link
        }
        dict_list.append(new_dict)
        index += 1
    print(f'{len(dict_list)} total healthcare workers')
    print(f'{no_link_count} have no link')
    return dict_list

print('Scraping...')
DICT_LIST = scrape()
ALL_DATA = pd.DataFrame(DICT_LIST)
USA_DATA = ALL_DATA[ALL_DATA.COUNTRY == 'USA']
ALL_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_{TODAY}.csv', index=False)
USA_DATA.to_csv(f'{OUT_DIRECTORY}Memorium_USA_{TODAY}.csv', index=False)
