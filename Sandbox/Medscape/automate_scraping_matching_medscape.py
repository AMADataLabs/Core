'''
This script scrapes the Medscape In Memorium feature
'''
from datetime import date, timedelta
import json
import os
from nameparser import HumanName
import pandas as pd
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import settings
from process_me import remove_processed_mes
from spec_match import get_spec_table, match_spec

YESTERDAY = str(date.today() - timedelta(days=1))

#Set today
TODAY = str(date.today())

#Set directories
PPD_FILE = os.environ.get('PPD_FILE')
OUT = os.environ.get('OUT_DIR')
print(OUT)
OUT_DIRECTORY = f'{OUT}{TODAY}'
OUT_DIRECTORY_YESTERDAY = f'{OUT}{YESTERDAY}'
os.mkdir(OUT_DIRECTORY)

def newest_delta(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

#Define ppd
print('Reading PPD...')
PPD = pd.read_csv(PPD_FILE, low_memory=False)

def scrape():
    '''Scrapes the medscape in memorium page'''
    med_url = 'https://www.medscape.com/viewarticle/927976#vp_1'
    response = requests.get(med_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_text = soup.text

    with open(f'{OUT_DIRECTORY}/Memorium_Text_{TODAY}.txt', 'w') as outfile:
        json.dump(all_text, outfile)

    all_pars = soup.find_all('p')
    return all_pars

def get_states():
    '''Define state list'''
    states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
              "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
              "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
              "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
              "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
              "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
              "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
              "Puerto Rico", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",
              "Wyoming"]
    return states


def grab_data():
    '''Extract relevant data from soup'''
    no_link_count = 0
    states = get_states()
    data = scrape()
    dict_list = []
    for paragraph in data[6:-10]:
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
            if ',' in paragraph.text:
                print('Human intervention needed for the following exception:')
                print(index_error)
                print(paragraph)
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
        dict_list.append(new_dict)
    return dict_list


print('Scraping...')
DICT_LIST = grab_data()
ALL_DATA = pd.DataFrame(DICT_LIST)
USA_DATA = ALL_DATA[ALL_DATA.COUNTRY == 'USA']
ALL_DATA.to_csv(f'{OUT_DIRECTORY}/Memorium_{TODAY}.csv', index=False)
USA_DATA.to_csv(f'{OUT_DIRECTORY}/Memorium_USA_{TODAY}.csv', index=False)


def split_names(roster_df):
    '''Splits name column into components'''
    roster_df = roster_df.drop_duplicates()
    dict_list = []
    for row in roster_df.itertuples():
        name_parsed = HumanName(row.NAME)
        name_dict = {
            'NAME': row.NAME,
            'FIRST_NAME': name_parsed.first.upper(),
            'LAST_NAME': name_parsed.last.upper(),
            'MIDDLE_NAME': name_parsed.middle.upper(),
            'SUFFIX': name_parsed.suffix.upper(),
            'NICKNAME': name_parsed.nickname.upper(),
            'TITLE': name_parsed.title.upper(),
        }
        dict_list.append(name_dict)
    name_df = pd.DataFrame(dict_list)
    new_df = pd.merge(name_df, roster_df, on='NAME')
    return new_df


def fix_me(me_list):
    '''Add leading zeroes to ME numbers'''
    nums = []
    for num in me_list:
        num = str(num)
        num = num.replace('.0', '')
        if len(num) == 10:
            num = '0' + num
        elif len(num) == 9:
            num = '00' + num
        elif len(num) == 8:
            num = '000' + num
        nums.append(num)
    return nums


def append_me(roster_df, spec_df):
    '''Matches to PPD and appends ME'''
    data_split = split_names(roster_df)

    bad_spec_words = [
        'Nurse',
        'Vet',
        'Transport',
        'Assistant',
        'Receptionist',
        'Technician'
    ]
    mes = []
    for row in data_split.itertuples():
        physician_me = 'None'
        keep = True
        for word in bad_spec_words:
            if word in row.SPECIALTY:
                keep = False
        if keep:
            try:
                years = [2019.0 - int(row.AGE), 2020.0 - int(row.AGE)]
            except ValueError:
                pass
            new_df = PPD[(PPD.FIRST_NAME == row.FIRST_NAME) & (PPD.LAST_NAME == row.LAST_NAME)]
            if len(new_df) == 0 and years:
                if '-' in row.LAST_NAME:
                    last = row.LAST_NAME.replace('-', ' ')
                else:
                    last = row.LAST_NAME.replace(' ', '')
                new_df = PPD[(PPD.LAST_NAME == last) & (PPD.BIRTH_YEAR.isin(years))]
                if len(new_df) == 0:
                    pass
                if len(new_df) > 1:
                    new_df = new_df[new_df.CITY == row.CITY.upper()]
            elif len(new_df) > 1 and years:
                new_df = new_df[new_df.BIRTH_YEAR.isin(years)]
                if len(new_df) > 1:
                    new_df = new_df[new_df.CITY == row.CITY.upper()]   
            if len(new_df) == 1:
                if match_spec(new_df, row.SPECIALTY, spec_df):
                    physician_me = new_df.iloc[0]['ME']
            elif len(new_df) > 1:
                print(f'{row.NAME} potentially matched to multiple ME numbers.')

        mes.append(physician_me)

    data_split['ME'] = fix_me(mes)
    data_me = data_split[data_split.ME != 'None']
    return data_split, data_me


print('Matching and appending ME numbers...')
SPEC_DF = get_spec_table()
US_DATA_SPLIT, US_DATA_ME = append_me(USA_DATA, SPEC_DF)
US_DATA_ME.to_excel(f'{OUT_DIRECTORY}/Memorium_USA_Physicians_{TODAY}.xlsx', index=False)
US_DATA_SPLIT.to_excel(f'{OUT_DIRECTORY}/Memorium_USA_ME_{TODAY}.xlsx', index=False)


def get_counts(dataframe):
    '''GET COUNTS'''
    nurse = 0
    tech = 0
    assistant = 0
    admin = 0
    other = 0
    phys = 0
    eight = 0
    seven = 0
    six = 0
    five = 0
    four = 0
    three = 0
    two = 0
    unk = 0

    for row in dataframe.itertuples():
        if 'Nurse' in row.SPECIALTY:
            nurse += 1
        elif 'Tech' in row.SPECIALTY:
            tech += 1
        elif 'Assistant' in row.SPECIALTY:
            assistant += 1
        elif 'Admin' in row.SPECIALTY:
            admin += 1
        elif row.ME != 'None':
            phys += 1
        else:
            other += 1
        if row.AGE.isnumeric():
            age = int(row.AGE)
            if age >= 80:
                eight += 1
            elif age >= 70:
                seven += 1
            elif age >= 60:
                six += 1
            elif age >= 50:
                five += 1
            elif age >= 40:
                four += 1
            elif age >= 30:
                three += 1
            else:
                two += 1
        else:
            unk += 1
    role_df = pd.DataFrame({'Role': ['Physician', 'Nurse', 'Technician', 'PA', 'Administration',
                                     'Other'], 'Count': [phys, nurse, tech, assistant, admin,
                                                         other]})
    role_plt = role_df.plot.bar(x='Role', y='Count', rot=0,
                                title='COVID-19 Healthcare Worker Fatalities by Role - USA',
                                color='darkorchid')
    age_df = pd.DataFrame({'Age': ['80 and older', '70-79', '60-69', '50-59', '40-49', '30-39',
                                   'under 30', 'Unknown'], 'Count': [eight, seven, six, five, four,
                                                                     three, two, unk]})
    return (role_df, role_plt, age_df)

ROLE_DF, ROLE_PLT, AGE_DF = get_counts(US_DATA_SPLIT)
plt.savefig(f'{OUT_DIRECTORY}/ROLE_{TODAY}.png')
plt.close()
STATE_DF = US_DATA_SPLIT.groupby('STATE').count()['NAME'].sort_values(ascending=False)
STATE_PLT = STATE_DF.plot.bar(title='COVID-19 Healthcare Worker Fatalities by State - USA',
                              color='darkorchid', figsize=(15, 10), rot=45, legend=False)
plt.savefig(f'{OUT_DIRECTORY}/STATE_{TODAY}.png')
plt.close()
COUNTRY_DF = ALL_DATA.groupby('COUNTRY').count()['NAME'].sort_values(ascending=False)
COUNTRY_PLT = COUNTRY_DF.plot.bar(title='COVID-19 Healthcare Worker Fatalities by Country',
                                  color='darkorchid', figsize=(15, 10), rot=45, legend=False)
plt.savefig(f'{OUT_DIRECTORY}/COUNTRY_{TODAY}.png')
plt.close()
AGE_DF_2 = US_DATA_SPLIT[(US_DATA_SPLIT.AGE != 'age unknown') 
                         & (US_DATA_SPLIT.AGE != 'None')][['NAME', 'AGE']]
AGE_DF_2['AGE'] = AGE_DF_2.AGE.astype(int)
AGE_PLT = AGE_DF_2.hist(color='darkorchid')
plt.savefig(f'{OUT_DIRECTORY}/AGE_{TODAY}.png')
plt.close()

with pd.ExcelWriter(f'{OUT_DIRECTORY}/USA_Stats_{TODAY}.xlsx') as writer:
    STATE_DF.to_excel(writer, sheet_name='By State - US')
    ROLE_DF.to_excel(writer, sheet_name='By Role - US', index=False)
    AGE_DF.to_excel(writer, sheet_name='By Age - US', index=False)
    COUNTRY_DF.to_excel(writer, sheet_name='By Country')

US_YESTERDAY = newest_delta(OUT_DIRECTORY_YESTERDAY, f'USA_ME_{YESTERDAY}')
ALL_YESTERDAY = newest_delta(OUT_DIRECTORY_YESTERDAY, f'Memorium_{YESTERDAY}')

US_DATA_YESTERDAY = pd.read_excel(US_YESTERDAY)
ALL_DATA_YESTERDAY = pd.read_csv(ALL_YESTERDAY)

INTERSECT_US = list(pd.merge(US_DATA_SPLIT, US_DATA_YESTERDAY, on=['NAME',
                                                                   'AGE',
                                                                   'SPECIALTY',
                                                                   'LOCATION',
                                                                   'CITY',
                                                                   'STATE',
                                                                   'COUNTRY'
                                                                   ])['NAME'])
US_DELTA = US_DATA_SPLIT[US_DATA_SPLIT.NAME.isin(INTERSECT_US) == False]

INTERSECT_ALL = list(pd.merge(ALL_DATA, ALL_DATA_YESTERDAY, on=['NAME',
                                                                'AGE',
                                                                'SPECIALTY',
                                                                'LOCATION',
                                                                'CITY',
                                                                'STATE',
                                                                'COUNTRY'
                                                                ])['NAME'])
ALL_DELTA = ALL_DATA[ALL_DATA.NAME.isin(INTERSECT_ALL) == False]

US_DELTA.to_csv(f'{OUT_DIRECTORY}/Memorium_USA_Delta_{TODAY}.csv', index=False)
ALL_DELTA.to_csv(f'{OUT_DIRECTORY}/Memorium_World_Delta_{TODAY}.csv', index=False)

UNPROCESSED = remove_processed_mes(US_DATA_ME)
UNPROCESSED.to_excel(f'{OUT_DIRECTORY}/Memorium_USA_Physicians_Unprocessed_{TODAY}.xlsx',
                     index=False)
