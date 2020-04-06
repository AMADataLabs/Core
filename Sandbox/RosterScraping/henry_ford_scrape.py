'''
This script scrapes the Henry Ford Health System Roster
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

NUM_LIST = list(range(1, 474))

DICT_LIST = []
TEXT_LIST = []
for num in NUM_LIST:
    base_url = f'''
    https://www.henryford.com/physician-directory/search-results?page={num}&zip=&specialties=
    '''
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    TEXT_LIST.append(soup.text)
    listings = soup.find_all(class_='listing')
    for listing in listings:
        link = listing.find('a')['href']
        try:
            phone = listing.find(class_='phones').text
        except:
            phone = 'None'
        try:
            specialty = listing.find(class_='module-pd-specialty-list').text
            specialty = specialty.replace('\n', '').replace('Specialties: ', '')
        except:
            specialty = 'None'
        try:
            name = listing.find('img')['alt']
        except:
            name = 'None'
        print(f"{name} is done!")
        offices = listing.find_all(class_='module-pd-office-item')
        office_names = []
        office_addresses = []
        for office in offices:
            try:
                office_names.append(office.find(class_='office-detail').text.replace('\n', ''))
            except:
                office_names.append('None')
            try:
                office_addresses.append(office.find(class_='map')['href'].split('=')[1])
            except:
                office_addresses.append('None')
        new_dict = {
            'Link': link,
            'Name': name,
            'Specialty': specialty,
            'Phone': phone,
            'Offices': office_names,
            'Addresses': office_addresses
        }
        DICT_LIST.append(new_dict)
    print(f'Page {num} is done!')


with open(f'{OUT_DIRECTORY}Henry_Ford_Text_{TODAY}.txt', 'w') as outfile:
    json.dump(TEXT_LIST, outfile)

pd.DataFrame(DICT_LIST).to_csv(f'{OUT_DIRECTORY}Henry_Ford_Scrape_{TODAY}.csv', index=False)
