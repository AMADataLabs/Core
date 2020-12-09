'''Tweets'''
import GetOldTweets3 as got
import pandas as pd
from nameparser import HumanName

def get_tweets():
    '''Get tweets'''
    username = 'CTZebra'
    count = 2000
    # Creation of query object
    tweetCriteria = got.manager.TweetCriteria().setUsername(username)\
                                        .setMaxTweets(count)
    # Creation of list that contains all tweets
    tweets = got.manager.TweetManager.getTweets(tweetCriteria)
    # Creating list of chosen tweet data
    user_tweets = [[tweet.date, tweet.text] for tweet in tweets]
    return user_tweets

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

def get_state_list():
    '''List of state names and abbreviations'''
    return ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
                    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", 
                    "Illinois","Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", 
                    "Maryland","Massachusetts", "Michigan", "Minnesota", "Mississippi", 
                    "Missouri", "Montana","Nebraska", "Nevada", "New Hampshire", "New Jersey", 
                    "New Mexico", "New York","North Carolina", "North Dakota", "Ohio", "Oklahoma", 
                    "Oregon", "Pennsylvania","Rhode Island", "South Carolina", "South Dakota", 
                    "Tennessee", "Texas", "Utah","Puerto Rico", "Vermont", "Virginia", "Washington", 
                    "West Virginia", "Wisconsin","Wyoming"]

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

def parse_tweets(tweet_list):
    '''Parse tweet list'''
    states = get_state_list()
    state_dict = get_state_dict()
    dict_list = []
    for tweet in tweet_list:
        name = 'None'
        age = 'None'
        date = 'None'
        link = 'None'
        state = 'None'
        date = tweet[0].strftime('%m-%d-%Y')
        name_split = tweet[1].split(',')
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
        sentence_list = tweet[1].split(' ')
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
    tweet_dict_list = parse_tweets(tweet_list)
    tweet_df = pd.DataFrame(tweet_dict_list)
    tweet_df = tweet_df[tweet_df['NAME'] != 'None']
    split_tweets = split_names(tweet_df).drop_duplicates()
    doctor_tweets = split_tweets[(split_tweets['TITLE'] == 'DR.')]
    return (split_tweets, doctor_tweets)
