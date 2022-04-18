'''HelpTheHeroes'''
import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_soup():
    '''Get soup'''
    url = 'https://www.helptheheroes.net/In-Memoriam'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_states():
    '''Get state list'''
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
              "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
              "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
              "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
              "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
              "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
              "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
              "Puerto Rico", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", 
              "Wyoming"]
    return (states)

def one_entry(paragraph, states):
    'Get one entry'''
    if paragraph.text == "\xa0":
        print('Empty')
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
        link = 'None'
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
        'LOCATION': location,
        'LINK': link
        }
    return new_dict

def grab_data(soup):
    '''Grab data'''
    states = get_states()
    dict_list = []
    pars = soup.find_all('h4')
    for paragraph in pars[1:]:
        new_dict = one_entry(paragraph, states)
        dict_list.append(new_dict)
    return dict_list

def hero_scrape():
    '''Main function'''
    hero_data = get_soup()
    heroes = pd.DataFrame(grab_data(hero_data))
    return heroes
