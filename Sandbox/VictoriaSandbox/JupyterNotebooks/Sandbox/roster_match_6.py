import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from nameparser import HumanName

def split_names(df):
    dict_list = []
    for row in df.itertuples():
        name_parsed = HumanName(row.NAME)
        name_dict = {
        'NAME':row.NAME,
        'FIRST_NAME': name_parsed.first.upper(),
        'LAST_NAME': name_parsed.last.upper(),
        'MIDDLE_NAME': name_parsed.middle.upper(),
        'SUFFIX':name_parsed.suffix.upper(),
        'NICKNAME':name_parsed.nickname.upper()
        }
        dict_list.append(name_dict)
    name_df = pd.DataFrame(dict_list)
    new_df = pd.merge(name_df, df, on = 'NAME')
    return(new_df)

def match_ppd_name(ppd,df):
    count = len(df)
    matched = pd.merge(ppd, df, on = ['FIRST_NAME','LAST_NAME'], how = 'right')
    names = []
    duplicate_names = []
    missing_names =[]
    for row in matched.itertuples():
        if row.NAME not in names:
            names.append(row.NAME)
        elif row.NAME not in duplicate_names:
            duplicate_names.append(row.NAME)
        if pd.isna(row.ME)==True:
            missing_names.append(row.NAME)
    
    duplicates = matched[matched.NAME.isin(duplicate_names)]
    matched = matched.drop_duplicates('NAME', keep = False)
    
    print(f'{len(duplicates)} duplicates found.')
    print(f'{len(missing_names)} names missing.')
    
    return(duplicates, missing_names, matched)

def count_matches(matched_df):
    names = []
    duplicate_names = []
    for row in matched_df.itertuples():
        if row.NAME not in names:
            names.append(row.NAME)
        elif row.NAME not in duplicate_names:
            duplicate_names.append(row.NAME)
    
    duplicates = matched_df[matched_df.NAME.isin(duplicate_names)]
    matched = matched_df.drop_duplicates('NAME', keep = False)
    
    print(f'{len(duplicates)} duplicates found.')
    print(f'{len(matched)} unique matches found.')
    
    return(duplicates, matched)

def match_ppd_state(matched_df):
    state_match_list = []
    for row in matched_df.itertuples():
        state_match = False
        if row.POLO_STATE == row.LOCATION_ADDRESS_STATE:
            state_match = True
        state_match_list.append(state_match)
    matched_df['STATE_MATCH']=state_match_list
    matched_df = matched_df[matched_df['STATE_MATCH']==True]
    return(matched_df)
        
def match_ppd_city(matched_df):
    city_match_list = []
    for row in matched_df.itertuples():
        city_match = False
        if row.POLO_CITY == row.LOCATION_ADDRESS_CITY.upper():
            city_match = True
        city_match_list.append(city_match)
    matched_df['CITY_MATCH']=city_match_list
    matched_df = matched_df[matched_df['CITY_MATCH']==True]
    return(matched_df)

def match_ppd_middle(matched_df):
    middle_match_list =[]
    for row in matched_df.itertuples():
        mid_match = False
        if row.MIDDLE_NAME_y != 'None':
            print(row.MIDDLE_NAME_y)
            print(row.MIDDLE_NAME_x)
            if row.MIDDLE_NAME_x == row.MIDDLE_NAME_y:
                mid_match = True
            elif len(row.MIDDLE_NAME_x)>0 and len(row.MIDDLE_NAME_y)>0:
                if row.MIDDLE_NAME_x[0] == row.MIDDLE_NAME_y[0]:
                    mid_match = True
        middle_match_list.append(mid_match)
    matched_df['MID_MATCH']=middle_match_list
    matched_df = matched_df[matched_df['MID_MATCH']==True]
    return(matched_df)
def check_match(thing_1, thing_2):
    keep = False
    if fuzz.ratio(thing_1.upper(), thing_2) > 80:
            keep = True
    elif thing_2 in thing_1.upper():
        keep = True
    elif thing_1.upper() in thing_2:
        keep = True
    return keep
    
def match_ppd_spec_fuzzy(matched_df):
    keep_list = []
    for row in matched_df.itertuples():
        keep = check_match(row.DEPARTMENT.upper(), row.DESC_PRIM)
        if keep ==  False:
            for title in row.TITLES:
                if keep == False:
                    keep = check_match(title, row.DESC_PRIM)
        keep_list.append(keep)
    matched_df['SPEC_MATCH']=keep_list
    matched_df = matched_df[matched_df['SPEC_MATCH']==True]
    return(matched_df)

def match(brig, ppd):
    brig_df = split_names(brig)
    brig_df = brig_df.drop_duplicates('NAME')

    duplicate_names_brig, missing_names_brig, matched_brig = match_ppd_name(ppd, brig_df)
    new_matched = match_ppd_spec_fuzzy(duplicate_names_brig)
    new_matched.head()
    new_duplicates, new_matches = count_matches(new_matched)
    new_matches.head()
    print(len(matched_brig))
    matched_brig = matched_brig.append(new_matches)
    print(len(matched_brig))
    print(f'{len(new_matches)} new matches confirmed. {len(matched_brig)} total matches confirmed.')

    new_matched_2 = match_ppd_state(new_duplicates)
    new_duplicates_2, new_matches_2 = count_matches(new_matched_2)
    print(len(matched_brig))
    matched_brig = matched_brig.append(new_matches_2)
    print(len(matched_brig))
    print(f'{len(new_matches_2)} new matches confirmed. {len(matched_brig)} total matches confirmed.')

    new_matched_3 = match_ppd_city(new_duplicates_2)
    new_duplicates_3, new_matches_3 = count_matches(new_matched_3)
    matched_brig = matched_brig.append(new_matches_3)
    print(f'{len(new_matches_3)} new matches confirmed. {len(matched_brig)} total matches confirmed.')

    new_matched_4 = match_ppd_middle(new_duplicates_3)
    new_duplicates_4, new_matches_4 = count_matches(new_matched_4)
    matched_brig = matched_brig.append(new_matches_4)
    print(f'{len(new_matches_4)} new matches confirmed. {len(matched_brig)} total matches confirmed.')

    return(matched_brig, missing_names_brig, new_duplicates_4)