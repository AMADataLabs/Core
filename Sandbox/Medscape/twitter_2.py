'''Tweets'''
import pandas as pd
from nameparser import HumanName
from bs4 import BeautifulSoup
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime

def get_url():
    today_date = datetime.today()
    since = (today_date - relativedelta(days=5)).strftime("%Y-%m-%d")
    url = f'https://mobile.twitter.com/search?f=live&q=(from%3ACTZebra)%20since%3A{since}%20-filter%3Areplies'
    return url

def get_tweets():
    '''Get tweets'''
    url = get_url()
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
    tweets = soup.find_all(class_='tweet')
    return tweets

def split_names(roster_df):
    #Splits name column into components
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

def get_tweet_text(tweets):
    '''Extract info from tweet html'''
    dict_list = []
    for twit in tweets:
        date = twit.find(class_='timestamp').text.replace('\n','')
        tweet_text = twit.find(class_='tweet-text').text.replace('\n','').replace('  ','')
        if tweet_text[0]==' ':
            tweet_text = tweet_text[1:]
        try:
            link = twit.find(class_='twitter_external_link')['data-expanded-url']
        except:
            link = 'None'
        new_dict = {
            'Date': date,
            'Tweet_Text': tweet_text,
            'Link': link
        }
        dict_list.append(new_dict)
    return dict_list

def parse_tweets(tweet_dict_list):
    '''Parse tweet list'''
    state_dict = get_state_dict()
    states = list(state_dict.keys()) + list(state_dict.values())
    dict_list = []
    for twit in tweet_dict_list:
        name = 'None'
        age = 'None'
        date = twit['Date']
        link = twit['Link']
        state = 'None'
        tweet = twit['Tweet_Text']
        name_split = tweet.split(',')
        if len(name_split) > 1:
            name = name_split[0]
            try:
                name_list = name.split(' ')
                if name.isnumeric() or name_list[1][0].islower():
                    name = 'None'
                elif len(name_list) > 5 or name_list[1][0].isnumeric():
                    name = 'None'
            except:
                name = 'None'
            age = name_split[1][1:3]
            if age.isnumeric() == False:
                age = 'None'
        sentence_list = tweet.split(' ')
        for word in sentence_list:
            if 'http' in word:
                link = word
            else:
                word = word.replace(',', '').replace('.', '')
            if word in states:
                if word in state_dict.keys():
                    state = state_dict[word]
                else:
                    state = word
        new_dict = {
            'NAME': name,
            'AGE': age,
            'DATE':date,
            'STATE':state,
            'LINK': link
        }
        dict_list.append(new_dict)
    return dict_list

def twitter_scrape():
    '''Scrape Twitter'''
    tweet_list = get_tweets()
    tweet_dict_list = get_tweet_text(tweet_list)
    tweet_dict_list = parse_tweets(tweet_dict_list)
    tweet_df = pd.DataFrame(tweet_dict_list)
    tweet_df = tweet_df[tweet_df['NAME'] != 'None']
    split_tweets = split_names(tweet_df).drop_duplicates()
    doctor_tweets = split_tweets[(split_tweets['TITLE'] == 'DR.')]
    return (split_tweets, doctor_tweets)