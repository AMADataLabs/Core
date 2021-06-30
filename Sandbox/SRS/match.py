import pandas as pd
from nameparser import HumanName
from fuzzywuzzy import fuzz

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
    criteria_list = [['first_middle','last_nm','birth_dt'],
                    ['FIRST','LAST', 'birth_dt'],
                    ['FIRST', 'gender','birth_dt', 'birth_state_cd'],
                    ['LAST', 'gender','birth_dt', 'birth_state_cd']]
    return criteria_list

def match_process(all_students, unmatched):
    criteria_list = get_criteria()
    matched = pd.DataFrame({'entity_id':[], 'AAMC ID':[]})
    for criteria in criteria_list:
        unmatched, matched = match(criteria, all_students, unmatched, matched)
    return (matched, unmatched)

def last_ditch(unmatched, all_students, matched):
    FUCKIT = pd.merge(all_students, unmatched, on=['gender','birth_dt'])
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
    no_id['gender']=no_id.Sex
    get_full_names(all_students)
    get_full_names(no_id)
    parse_names(all_students)
    parse_names(no_id)
    matched, unmatched = match_process(all_students, no_id)
    matched = last_ditch(unmatched, all_students, matched)
    return matched


