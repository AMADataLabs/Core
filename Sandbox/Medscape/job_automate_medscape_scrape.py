'''
This script scrapes the Medscape In Memorium feature
'''
from datetime import datetime, date
import pandas as pd
from nameparser import HumanName
#from medscape_scrape import scrape
from datetime import datetime
import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os

#Set today
TODAY = str(date.today())
#Set Output Directory
OUT_DIRECTORY = f'C:/Users/nkhatri/OneDrive - American Medical Association/Documents/Task-Scheduled/{TODAY}'
os.mkdir(OUT_DIRECTORY)
#Define ppd
PPD_FILE = 'C:/Users/nkhatri/OneDrive - American Medical Association/Documents/Task-Scheduled/ppd_data_20200404.csv'
print('Reading PPD...')
PPD = pd.read_csv(PPD_FILE)

def scrape():
    '''Scrapes the medscape in memorium page'''
    med_url = 'https://www.medscape.com/viewarticle/927976#vp_1'
    response = requests.get(med_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_text = soup.text

    with open(f'{OUT_DIRECTORY}/Memorium_Text_{TODAY}.txt', 'w') as outfile:
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
ALL_DATA.to_csv(f'{OUT_DIRECTORY}/Memorium_{TODAY}.csv', index=False)
USA_DATA.to_csv(f'{OUT_DIRECTORY}/Memorium_USA_{TODAY}.csv', index=False)

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
USA_DATA_ME.to_csv(f'{OUT_DIRECTORY}/Memorium_USA_Physicians_{TODAY}.csv', index=False)
USA_DATA_SPLIT.to_csv(f'{OUT_DIRECTORY}/Memorium_USA_ME_{TODAY}.csv', index=False)

def newest(path):
    '''Grabs newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if 'USA_ME' in basename]
    return max(paths, key=os.path.getctime)

RESULT_DIR = newest(OUT_DIRECTORY)
print(RESULT_DIR)
DATA = pd.read_csv(RESULT_DIR)

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
    role_df = pd.DataFrame({'Role':['Physician', 'Nurse', 'Technician', 'PA', 'Administration',
                                    'Other'], 'Count':[phys, nurse, tech, assistant, admin, other]})
    role_plt = role_df.plot.bar(x='Role', y='Count', rot=0,
                                title='COVID-19 Healthcare Worker Fatalities by Role',
                                color='darkorchid')
    age_df = pd.DataFrame({'Age':['80 and older', '70-79', '60-69', '50-59', '40-49', '30-39',
                                  'under 30', 'Unknown'], 'Count':[eight, seven, six, five, four,
                                                                   three, two, unk]})
    age_plt = age_df.plot.bar(x='Age', y='Count', rot=0,
                              title='COVID-19 Healthcare Worker Fatalities by Age',
                              color='darkorchid')
    return(role_df, role_plt, age_df, age_plt)

ROLE_DF, ROLE_PLT, AGE_DF, AGE_PLT = get_counts(DATA)
STATE_DF = DATA.groupby('STATE').count()['NAME']
STATE_PLT = STATE_DF.plot.bar(title='COVID-19 Healthcare Worker Fatalities by State',
                              color='darkorchid')

with pd.ExcelWriter(f'{OUT_DIRECTORY}/USA_Stats_{TODAY}.xlsx') as writer:
    STATE_DF.to_excel(writer, sheet_name='By State')
    ROLE_DF.to_excel(writer, sheet_name='By Role', index=False)
    AGE_DF.to_excel(writer, sheet_name='By Age', index=False)

FIG_1 = AGE_PLT.get_figure()
FIG_1.savefig(f'{OUT_DIRECTORY}/AGE_{TODAY}.png')
FIG_2 = ROLE_PLT.get_figure()
FIG_2.savefig(f'{OUT_DIRECTORY}/ROLE_{TODAY}.png')
FIG_3 = STATE_PLT.get_figure()
FIG_3.savefig(f'{OUT_DIRECTORY}/STATE_{TODAY}.png')
