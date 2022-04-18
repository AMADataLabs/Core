'''Define scraping functions'''
from bs4 import BeautifulSoup
import requests

def get_soup(base_url):
    '''Get soup from url'''
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_state_dict():
    '''Dictionary of state names and abbreviations'''
    return {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands':'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }

def get_city_dict():
    return {'Cincinnati':'OH',
            'Chicago':'IL',
            'Detroit':'MI',
            'Cleveland':'OH',
            'Philadelphia':'PA',
            'Phoenix':'AZ',
            'Boston':'MA',
            'Sacramento':'CA',
            'Dallas':'TX'}

def is_city(word):
    '''Get state from city'''
    cities = get_city_dict()
    for city in cities.keys():
        if city in word:
            return cities[city]
    return False

def get_state_list():
    '''List of state names and abbreviations'''
    return ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
            "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
            "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
            "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
            "Puerto Rico", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin",
            "Wyoming",'WVa']

def get_worker_words():
    '''Worker words'''
    return [
        'staffers',
        'employees',
        'workers',
        'people',
        'individuals',
        'caregivers',
        'of',
        'nonclinical',
        'staff'
    ]

def get_months():
    '''Month list'''
    return [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]

def convert_state(state):
    '''Convert state into abbreviation'''
    us_state_abbrev = get_state_dict()
    if state in us_state_abbrev.keys():
        state = us_state_abbrev[state]
    return state

def is_state(word):
    '''Check if word is a state, return state abbrevation if so'''
    states = get_state_list()
    word = word.replace('.', '').replace('(', '').replace(')', '').replace(',','')
    if word == 'Fla':
        return('FL')
    for state in states:
        if state[0:3] == word[0:3]:
            return convert_state(state)
        elif state == word:
            return convert_state(state)
        elif state.title() == word:
            return convert_state(state)
    return False

def is_month(string):
    '''Check if word is month'''
    months = get_months()
    for month in months:
        if month in string:
            return True
    return False

def is_worker(word):
    '''Check if word is worker'''
    worker_words = get_worker_words()
    for worker_word in worker_words:
        if worker_word in word:
            return True
    return False

def find_furloughs(paragraph):
    '''Find furlough count in paragraph'''
    sentences = paragraph.text.split('. ')
    for sentence in sentences:
        if 'furlough' in sentence:
            words = sentence.split(' ')
            word_index = 0
            number = 'Unspecified'
            number_index = 0
            for word in words:
                if 'furlough' in word:
                    furlough_index = word_index
                try:
                    next_word = words[word_index+1]
                except IndexError:
                    next_word = 'None'
                if word.replace(',', '').replace('.', '').isnumeric() and is_worker(next_word):
                    if number == 'Unspecified':
                        number = word
                        number_index = word_index
                    elif abs(number_index - furlough_index) > abs(word_index - furlough_index):
                        number = word
                        number_index = word_index
                word_index += 1
            if number != 'Unspecified':
                return number
    return 'Unspecified'

def find_layoffs(paragraph):
    '''Find layoff count in paragraph'''
    sentences = paragraph.text.split('. ')
    for sentence in sentences:
        if 'lay' in sentence and 'off' in sentence:
            word_index = 0
            number = 'Unspecified'
            number_index = 0
            words = sentence.split(' ')
            for word in words:
                if 'off' in word:
                    layoff_index = word_index
                try:
                    next_word = words[word_index+1]
                except IndexError:
                    next_word = 'None'
                if word.replace(',', '').replace('.', '').isnumeric() and is_worker(next_word):
                    if number == 'None':
                        number = word
                        number_index = word_index
                    elif abs(number_index - layoff_index) > abs(word_index - layoff_index):
                        number = word
                        number_index = word_index
                word_index += 1
            if number != 'Unspecified':
                return number
    return 'Unspecified'

def extract_data(soup):
    '''Get data dictionary list from soup'''
    pars = soup.find_all('p')
    dict_list = []
    date = 'None'
    for par in pars[7:]:
        link = 'None'
        inner_date = 'None'
        state = 'Unspecified'
        index = par.text.split('.')[0]
        if is_month(index):
            date = par.strong.text
        if index.isnumeric():
            furloughs = find_furloughs(par)
            layoffs = find_layoffs(par)
            if par.strong:
                location = par.strong.text
                if location[0] == ' ':
                    location = location[1:]
            if par.a:
                link = par.a['href']
            words = par.text.split(' ')
            word_index = 0
            for word in words:
                try:
                    next_word = words[word_index+1]
                except IndexError:
                    next_word = 'None'
                if is_month(word):
                    if next_word.isnumeric():
                        inner_date = word + ' ' + words[word_index+1]
                elif is_state(word):
                    state = is_state(word)
                elif 'based' in word:
                    new = word.replace('based', '').replace('-', '')
                    if is_state(new):
                        state = is_state(new)
                elif is_city(word) and state == 'Unspecified':
                    state = is_city(word)
                word_index += 1
            new_dict = {
                'Date': date,
                'Furloughs': furloughs,
                'Layoffs': layoffs,
                'Location': location,
                'Link': link,
                'State': state
                }
            if inner_date != 'None':
                new_dict['Date'] = inner_date
            dict_list.append(new_dict)
    return dict_list
