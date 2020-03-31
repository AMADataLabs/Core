'''
This script scrapes Penn Medicine online roster
'''
from datetime import date
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests

#Set today
TODAY = str(date.today())

#Set Output Directory
OUT_DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Roster_Scraping/'

def get_links():
    '''
    Pulls links from Find A Doctor page
    '''
    abcs = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'
    abc_list = abcs.split(' ')

    dict_list = []
    text_list = []
    names_list = []
    for letter in abc_list:
        print(letter)
        base_url = f'''
        https://www.pennmedicine.org/providers?name={letter}&searchby=name&fadf=PennMedicine
        '''
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_list.append(soup.text)
        doctors = soup.find_all(class_='fad-listing__list-item')
        for doctor in doctors:
            specialty = 'None'
            programs = 'None'
            name = doctor.find_all('a')[1].text
            if name not in names_list:
                names_list.append(name)
                link = doctor.find('a')['href']
                title = doctor.find(class_="fad-listing__list-item-title-secondary").text
                title = title.replace('\n', '').replace('  ', '').replace('\r', '')
                for thing in doctor.find_all(class_='fad-listing__list-item-ul'):
                    if 'Specialty' in thing.text:
                        specialty = thing.text.replace('\n', '').replace('Specialty: ', '')
                    if 'Programs' in thing.text:
                        programs = thing.text.replace('\n', '').replace('Programs: ', '')
                try:
                    phone = doctor.find(class_='fad-provider-bio__btn')['href'].replace('tel:', '')
                except:
                    phone = 'None'
                try:
                    location = doctor.find(class_='fad-listing__list-item-ul--sm').text
                    location = location.replace('\n', '')
                except:
                    location = 'None'
                new_dict = {
                    'LINK': link,
                    'Name': name,
                    'Title': title,
                    'Specialty': specialty,
                    'Programs': programs,
                    'Phone': phone,
                    'Location': location
                }
                dict_list.append(new_dict)
    return(dict_list, text_list)

def get_location_info(link_df):
    '''
    Loops through links to get location info
    '''
    base_url = 'https://www.pennmedicine.org'
    link_list = list(link_df['LINK'])
    index = 0
    dict_list = []
    text_list = []
    for link in link_list:
        url = base_url + link
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_list.append(soup.text)
        big_name = 'None'
        address_2 = 'None'
        address_1 = 'None'
        city = 'None'
        state = 'None'
        zipcode = 'None'
        try:
            small_name = soup.find(class_='fad-listing__list-item-title').text.replace('\n', '')
        except:
            small_name = 'None'
        add = soup.find(class_='fad-listing__list-item-address')
        try:
            titles = add.find_all(class_='fad-listing__list-item-address-title')
        except:
            titles = []
        try:
            lines = add.find_all(class_='fad-listing__list-item-address-line')
        except:
            lines = []
        if len(titles) != 0:
            big_name = titles[0].text.replace('\r', '').replace('\n', '').replace('  ', '')
            address_2 = titles[1].text.replace('\r', '').replace('\n', '').replace('  ', '')
        if len(lines) != 0:
            address_1 = lines[0].text.replace('\r', '').replace('\n', '').replace('  ', '')
            city = lines[1].text.split(', ')[0].replace('\r', '').replace('\n', '').replace('  ', '')
            add_info = lines[1].text.split(', ')[1].split(' ')
            state = add_info[0].replace('\r', '').replace('\n', '').replace('  ', '')
            zipcode = add_info[1].replace('\r', '').replace('\n', '').replace('  ', '')
        new_dict = {
            'LINK': link,
            'LOCATION_NAME': big_name,
            'LOCATION_ADDRESS_1': address_1,
            'LOCATION_ADDRESS_CITY': city,
            'LOCATION_ADDRESS_STATE': state,
            'LOCATION_ADDRESS_ZIP': zipcode,
            'LOCATION_NAME_SPECIFIC': small_name,
            'LOCATION_ADDRESS_2': address_2
        }
        dict_list.append(new_dict)
        index += 1
        indexed_name = link_list[index].replace('/providers/profile/', '')
        indexed_name = indexed_name.replace('?fadf=pennmedicine', '').replace('-', ' ')
        print(indexed_name.title())
    return(dict_list, text_list)

LINKS, LINK_TEXT = get_links()
LINK_DF = pd.DataFrame(LINKS)
LOC_LIST, LOC_TEXT = get_location_info(LINK_DF)
LOC_DF = pd.DataFrame(LOC_LIST)

with open(f'{OUT_DIRECTORY}Penn_Link_Text_{TODAY}.txt', 'w') as outfile:
    json.dump(LINK_TEXT, outfile)

with open(f'{OUT_DIRECTORY}Penn_Loc_Text_{TODAY}.txt', 'w') as outfile:
    json.dump(LOC_TEXT, outfile)

pd.merge(LOC_DF, LINK_DF, on='LINK').to_csv(f'{OUT_DIRECTORY}Penn_Scrape_{TODAY}.csv', index=False)
