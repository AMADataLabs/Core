import pandas as pd
from nameparser import HumanName
from fuzzywuzzy import fuzz
from datetime import date

def get_states():
    us_state_abbrev = {
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
    return us_state_abbrev

def merge_name(all_students):
    first_middles = []
    for row in all_students.itertuples():
        first = row.first_nm.strip()
        if row.middle_nm != 'None':
            middle = ' '+ row.middle_nm.strip()
        else:
            middle = ''
        first_middle = first + middle
        first_middles.append(first_middle)
    all_students['first_middle'] = first_middles
    return(all_students)

def get_full_names(df):
    full_names_all = []
    for row in df.itertuples():
        full_names_all.append(row.first_middle.strip() + ' '+ row.last_nm.strip())
    df['FULL_NAME'] = full_names_all
    return df

def parse_names(df):
    df['TITLE'] = [HumanName(x).title for x in df.FULL_NAME]
    df['FIRST'] = [HumanName(x).first for x in df.FULL_NAME]
    df['MIDDLE'] = [HumanName(x).middle for x in df.FULL_NAME]
    df['LAST'] = [HumanName(x).last for x in df.FULL_NAME]
    df['SUFFIX'] = [HumanName(x).suffix for x in df.FULL_NAME]
    df['NICKNAME'] = [HumanName(x).nickname for x in df.FULL_NAME]
    return df

def match(criteria, all_students, unmatched, matched):
    new_matched = pd.merge(all_students, unmatched, on=criteria)[['entity_id','AAMC ID']].drop_duplicates('entity_id')
    match_list = list(new_matched['AAMC ID'])
    match_list += list(matched['AAMC ID'])
    unmatched = unmatched[unmatched['AAMC ID'].isin(match_list)==False]
    matched = pd.concat([new_matched, matched])
    return (unmatched, matched)

def get_criteria():
    criteria_list = [['first_middle','last_nm','birth'],
                    ['FIRST','LAST', 'birth'],
                    ['FIRST', 'gender','birth', 'birth_state_cd'],
                    ['LAST', 'gender','birth', 'birth_state_cd']]
    return criteria_list

def match_process(all_students, unmatched):
    criteria_list = get_criteria()
    matched = pd.DataFrame({'entity_id':[], 'AAMC ID':[]})
    for criteria in criteria_list:
        unmatched, matched = match(criteria, all_students, unmatched, matched)
    return (matched, unmatched)

def last_ditch(unmatched, all_students, matched):
    FUCKIT = pd.merge(all_students, unmatched, on=['gender','birth'])
    keeps = []
    for row in FUCKIT.itertuples():
        keep = False
        if fuzz.ratio(row.FULL_NAME_y, row.FULL_NAME_x) > 70:
            keep = True
        keeps.append(keep)
    FUCKIT['KEEP']=keeps
    new_matched = FUCKIT[FUCKIT.KEEP ==True][['entity_id', 'AAMC ID']]
    matched = pd.concat([new_matched, matched])
    return matched

def match_missing_ids(no_id, all_students):
    all_students = all_students.fillna('None')
    o_id = no_id.fillna('None')
    us_state_abbrev = get_states()
    no_id['first_middle'] = [x.split(', ')[1] for x in no_id.Name]
    no_id['last_nm'] = [x.split(', ')[0] for x in no_id.Name]
    no_id['birth_state_cd'] = [us_state_abbrev[x] if x in us_state_abbrev.keys() else x for x in no_id['Birth State']]
    no_id['birth'] = pd.to_datetime(no_id['Date of Birth']) 
    with_birth = all_students[all_students.birth_dt!='None']
    without_birth =  all_students[all_students.birth_dt=='None']
    with_birth['birth'] = pd.to_datetime([str(x).replace(' ','') for x in with_birth.birth_dt])
    without_birth['birth'] = date.today()
    all_students = pd.concat([with_birth, without_birth])
    all_students['birth'] = pd.to_datetime(all_students.birth)
    all_students = merge_name(all_students)
    no_id['gender']=no_id.Sex
    get_full_names(all_students)
    get_full_names(no_id)
    parse_names(all_students)
    parse_names(no_id)
    matched, unmatched = match_process(all_students, no_id)
    matched = last_ditch(unmatched, all_students, matched)
    return matched


