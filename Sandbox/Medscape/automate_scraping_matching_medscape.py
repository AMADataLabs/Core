'''
This script scrapes the Medscape In Memorium feature
'''
from datetime import date
import json
import os
from nameparser import HumanName
import pandas as pd
from bs4 import BeautifulSoup
import requests
import settings
from process_me import remove_processed_mes
from spec_match import get_spec_table, match_spec
from heroes import hero_scrape
from twitter_2 import twitter_scrape

def newest_delta(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def scrape():
    '''Scrapes the medscape in memorium page'''
    med_url = 'https://www.medscape.com/viewarticle/927976#vp_1'
    response = requests.get(med_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    all_text = soup.text
    all_pars = soup.find_all('p')
    return all_text, all_pars

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
    all_text, data = scrape()
    dict_list = []
    for paragraph in data[10:-10]:
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
        except (KeyError, TypeError):
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
                elif city != 'None':
                    specialty = info_list[1]
                    location = info_list[2]
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
            if specialty == 'Doctor' and 'Medical' not in location:
                specialty = location
                location = 'None'
            if country in states:
                state = country
                country = 'USA'
            if not str(age).isnumeric() and age != 'None' and age != 'age unknown':
                city = specialty
                specialty = age
                age = 'None'
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
    return (all_text, dict_list)

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

def append_me(roster_df, spec_df, ppd):
    '''Matches to PPD and appends ME'''
    from_twitter = False
    if 'DATE' in roster_df.columns or 'Date' in roster_df.columns:
        from_twitter = True
        data_split = roster_df
    else:
        data_split = split_names(roster_df)
    bad_spec_words = [
        'NURS',
        'VET',
        'TRANSPORT',
        'ASSISTANT',
        'RECEPTIONIST',
        'TECHNICIAN',
        'PARAMEDIC',
        'AIDE',
        'SOCIAL WORKER',
        'ENTREPRENEUR',
        'SERVICES',
        'GROUPHOME',
        'SECURITY',
        'PHARMACIST',
        'FIRE',
        'EMPLOYEE',
        'DEVELOPER',
        'PSYCHIATRIST',
        'ADMINISTRATOR',
        'LEADER',
        'LPN',
        'THERAPIST',
        'CLERK',
        'COUNSELOR',
        'ATTENDANT',
        'ADMIN',
        'SUPPLY',
        'CLEAN',
        'PRIEST',
        'STAFF',
        'INVESTIGATOR',
        'MRI',
        'EDUCATOR',
        'OFFICER',
        'MAINTENANCE',
        'CNA',
        'SUPERVISOR',
        'COORDINATOR',
        'SUPERVISOR',
        'TECHNOLOGIST',
        'MECHANIC',
        'EMT'
    ]
    mes = []
    for row in data_split.itertuples():
        physician_me = 'None'
        keep = True
        if not from_twitter:
            for word in bad_spec_words:
                if word in row.SPECIALTY.upper():
                    keep = False
        if keep:
            new_df = ppd[(ppd.FIRST_NAME == row.FIRST_NAME) & (ppd.LAST_NAME == row.LAST_NAME)]
            try:
                years = [2019.0 - int(row.AGE), 2020.0 - int(row.AGE)]
            except ValueError:
                years = []
                if len(new_df)>1:
                    if row.STATE == "New York":
                        new_df = new_df[new_df.POLO_STATE == 'NY']
                    elif not from_twitter:
                        new_df = new_df[new_df.POLO_CITY == row.CITY.upper()]
                    else:
                        new_df = new_df[new_df.STATE == row.STATE]
            if len(new_df) == 0 and len(years) > 0:
                if '-' in row.LAST_NAME:
                    last = row.LAST_NAME.replace('-', ' ')
                elif ' ' in row.LAST_NAME:
                    last = row.LAST_NAME.replace(' ', '')
                else:
                    last = row.LAST_NAME.replace('J', 'G')
                new_df = ppd[(ppd.LAST_NAME == last) & (ppd.BIRTH_YEAR.isin(years))]
                if len(new_df) == 0:
                    pass
                if len(new_df) > 1:
                    if from_twitter:
                        print(f'{row.NAME} potentially matched to multiple ME numbers.')
                        temp_first = f'{row.FIRST_NAME}E'
                        new_df = ppd[(ppd.LAST_NAME == last) & (ppd.BIRTH_YEAR.isin(years))& (ppd.FIRST_NAME == temp_first)]
                    else:
                        new_df = new_df[new_df.CITY == row.CITY.upper()]
            elif len(new_df) > 1 and len(years) > 0:
                new_df = new_df[new_df.BIRTH_YEAR.isin(years)]
                if len(new_df) > 1 and not from_twitter:
                    new_df = new_df[new_df.CITY == row.CITY.upper()]
            if len(new_df) == 1:
                if from_twitter:
                    physician_me = new_df.iloc[0]['ME']
                elif match_spec(new_df, row.SPECIALTY, spec_df):
                    physician_me = new_df.iloc[0]['ME']
            elif len(new_df) > 1:
                print(f'{row.NAME} potentially matched to multiple ME numbers.')
        if row.FIRST_NAME == "ASHRAF" and row.LAST_NAME == "ABDO":
            physician_me = 'None'
        mes.append(physician_me)

    data_split['ME'] = fix_me(mes)
    data_me = data_split[data_split.ME != 'None']
    return data_split, data_me

def clean_other(other):
    '''Clean other data'''
    other = other.fillna('None')
    other = other.drop_duplicates()
    me_date = other[['ME', 'DATE']]
    dict__list = []
    for row in other.itertuples():
        if 'SLEPIAN' in row.NAME_twitter.upper() or 'SLEPIAN' in row.NAME_hero.upper():
            continue
        if 'Dr. William "Bill" Cohen' in row.NAME_twitter:
            continue
        elif "fights-for-life" in row.LINK_twitter:
            continue
        me = row.ME
        if me == '04201730096':
            continue
        if row.NAME_twitter == 'None':
            name = row.NAME_hero
            first_name = row.FIRST_NAME_hero
            middle_name = row.MIDDLE_NAME_hero
            title = row.TITLE_hero
            nickname = row.NICKNAME_hero
            last_name = row.LAST_NAME_hero
            age = row.AGE_hero
            state = row.STATE_hero
        else:
            name = row.NAME_twitter
            first_name = row.FIRST_NAME_twitter
            middle_name = row.MIDDLE_NAME_twitter
            title = row.TITLE_twitter
            nickname = row.NICKNAME_twitter
            last_name = row.LAST_NAME_twitter
            age = row.AGE_twitter
            state = row.STATE_twitter
        if row.LINK_twitter == 'None':
            link = row.LINK_hero
        else:
            link = row.LINK_twitter
        new_dict = {
            'NAME':name,
            'FIRST_NAME':first_name,
            'MIDDLE_NAME': middle_name,
            'LAST_NAME': last_name,
            'NICKNAME': nickname,
            'TITLE': title,
            'AGE': age,
            'STATE': state,
            'LINK': link,
            'ME':me
        }
        dict__list.append(new_dict)
    cleaned = pd.DataFrame(dict__list)
    cleaned = pd.merge(me_date, cleaned, on='ME')
    return cleaned

def get_out(today):
    '''Create out directory'''
    out = os.environ.get('OUT_DIR')
    out_directory = f'{out}{today}'
    os.mkdir(out_directory)
    return out_directory

def get_ppd():
    '''Read ppd'''
    ppd_file = os.environ.get('PPD_FILE')
    ppd = pd.read_csv(ppd_file, low_memory=False)
    return ppd

def scrape_all(today, out_dir):
    '''Scrape all sites'''
    all_text, dict_list = grab_data()
    with open(f'{out_dir}/Memorium_Text_{today}.txt', 'w') as outfile:
        json.dump(all_text, outfile)
    all_data = pd.DataFrame(dict_list)
    usa_data = all_data[all_data.COUNTRY == 'USA']
    all_data.to_csv(f'{out_dir}/Memorium_{today}.csv', index=False)
    usa_data.to_csv(f'{out_dir}/Memorium_USA_{today}.csv', index=False)
    all_twitter, twitter_docs = twitter_scrape()
    twitter_docs.to_csv(f'{out_dir}/Twitter_Doctors_{today}.csv', index=False)
    heroes = hero_scrape()
    return (usa_data, twitter_docs, heroes)

def main():
    '''Does it all'''
    today = str(date.today())
    out_dir = get_out(today)
    print('Reading PPD...')
    ppd = get_ppd()
    print('Scraping...')
    usa_data, twitter_docs, heroes = scrape_all(today, out_dir)
    print('Matching and appending ME numbers...')
    spec_df = get_spec_table()
    us_data_split, us_data_me = append_me(usa_data, spec_df, ppd)
    us_data_me.to_excel(f'{out_dir}/Memorium_USA_Physicians_{today}.xlsx', index=False)
    us_data_split.to_excel(f'{out_dir}/Memorium_USA_ME_{today}.xlsx', index=False)
    twitter_split, twitter_me = append_me(twitter_docs, spec_df, ppd)
    heroes_split, heroes_me = append_me(heroes, spec_df, ppd)
    heroes_me.to_excel(f'{out_dir}/Heroes_Physicians_{today}.xlsx', index=False)
    twitter_me.to_excel(f'{out_dir}/Twitter_Physicians_{today}.xlsx', index=False)
    unprocessed = remove_processed_mes(us_data_me)
    unprocessed.to_excel(f'{out_dir}/Memorium_USA_Physicians_Unprocessed_{today}.xlsx',
                         index=False)
    other_me = pd.merge(twitter_me, heroes_me, on='ME', how='outer', suffixes=['_twitter', '_hero'])
    cleaned_other = clean_other(other_me)
    other_unprocessed = remove_processed_mes(cleaned_other)
    other_unprocessed.to_excel(f'{out_dir}/Other_Physicians_Unprocessed_{today}.xlsx',
                               index=False)

if __name__ == "__main__":
    main()
