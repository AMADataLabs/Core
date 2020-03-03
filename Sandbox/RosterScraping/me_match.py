'''
This script outlines the functions to match each physician in a roster dataframe to the ppd
'''
import pandas as pd
from fuzzywuzzy import fuzz
from nameparser import HumanName

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

def match_ppd_name(ppd, roster_df):
    '''
    Merges the ppd and the roster dataframe on physician name finds and returns
    dataframe of duplicates, dataframe of unique matches, and list of unmatched names
    '''
    matched = pd.merge(ppd, roster_df, on=['FIRST_NAME', 'LAST_NAME'], how='right')
    names = []
    duplicate_names = []
    missing_names = []
    for row in matched.itertuples():
        if row.NAME not in names:
            names.append(row.NAME)
        elif row.NAME not in duplicate_names:
            duplicate_names.append(row.NAME)
        if pd.isna(row.ME):
            missing_names.append(row.NAME)
    duplicates = matched[matched.NAME.isin(duplicate_names)]
    matched = matched.drop_duplicates('NAME', keep=False)
    print(f'{len(duplicates)} duplicates found.')
    print(f'{len(missing_names)} names missing.')
    return(duplicates, missing_names, matched)

def count_matches(matched_df):
    '''
    Splits a merged dataframe into a dataframe of suplicates and a dataframe of
    unique matches
    '''
    names = []
    duplicate_names = []
    for row in matched_df.itertuples():
        if row.NAME not in names:
            names.append(row.NAME)
        elif row.NAME not in duplicate_names:
            duplicate_names.append(row.NAME)
    duplicates = matched_df[matched_df.NAME.isin(duplicate_names)]
    matched = matched_df.drop_duplicates('NAME', keep=False)
    print(f'{len(duplicates)} duplicates found.')
    print(f'{len(matched)} unique matches found.')
    return(duplicates, matched)

def match_ppd_spec_fuzzy(matched_df):
    '''
    Removes rows of a merged dataframe in which the specialities do not roughly
    match
    '''
    keep_list = []
    for row in matched_df.itertuples():
        keep = False
        if fuzz.ratio(row.SPECIALTY.upper(), row.DESC_PRIM) > 80:
            keep = True
        elif row.DESC_PRIM in row.SPECIALTY.upper():
            keep = True
        elif row.SPECIALTY.upper() in row.DESC_PRIM:
            keep = True
        keep_list.append(keep)
    matched_df['SPEC_MATCH'] = keep_list
    matched_df = matched_df[matched_df['SPEC_MATCH']]
    return matched_df

def match_ppd_state(matched_df):
    '''
    Removes rows of a merged dataframe in which the states do not match
    '''
    state_match_list = []
    for row in matched_df.itertuples():
        state_match = False
        if row.POLO_STATE == row.LOCATION_ADDRESS_STATE:
            state_match = True
        state_match_list.append(state_match)
    matched_df['STATE_MATCH'] = state_match_list
    matched_df = matched_df[matched_df['STATE_MATCH']]
    return matched_df

def match_ppd_city(matched_df):
    '''
    Removes rows of a merged dataframe in which the cities do not match
    '''
    city_match_list = []
    for row in matched_df.itertuples():
        city_match = False
        if row.POLO_CITY == row.LOCATION_ADDRESS_CITY.upper():
            city_match = True
        city_match_list.append(city_match)
    matched_df['CITY_MATCH']=city_match_list
    matched_df = matched_df[matched_df['CITY_MATCH']]
    return matched_df

def match_ppd_middle(matched_df):
    '''
    Removes rows of a merged dataframe in which the cities do not match
    '''
    middle_match_list = []
    for row in matched_df.itertuples():
        mid_match = False
        if row.MIDDLE_NAME_y != 'None':
            if row.MIDDLE_NAME_x == row.MIDDLE_NAME_y:
                mid_match = True
            elif row.MIDDLE_NAME_x[0] == row.MIDDLE_NAME_y[0]:
                mid_match = True
        middle_match_list.append(mid_match)
    matched_df['MID_MATCH'] = middle_match_list
    matched_df = matched_df[matched_df['MID_MATCH']]
    return matched_df

def match_ppd_spec_hard(matched_df):
    '''
    Removes rows of a merged dataframe in which the speciaties do not exactly
    match
    '''
    spec_match_list = []
    for row in matched_df.itertuples():
        spec_match = False
        if row.DESC_PRIM == row.SPECIALTY.upper():
            spec_match = True
        spec_match_list.append(spec_match)
    matched_df['SPEC_MATCH'] = spec_match_list
    matched_df = matched_df[matched_df['SPEC_MATCH']]
    return matched_df

def find_missing_1(missing_df, ppd):
    '''
    Matches unmatched names to ppd entries by last name
    '''
    dict_list_1 = []
    for row in missing_df.itertuples():
        print(row.LAST_NAME)
        new_df = ppd[ppd.LAST_NAME == row.LAST_NAME]
        for line in new_df.itertuples():
            match = False
            if fuzz.ratio(row.FIRST_NAME, line.FIRST_NAME) > 85:
                match = True
            elif row.FIRST_NAME in line.FIRST_NAME:
                match = True
            elif row.MIDDLE_NAME == line.FIRST_NAME:
                match = True
            elif len(line.MIDDLE_NAME) > 4 and line.MIDDLE_NAME in row.FIRST_NAME:
                match = True
            elif row.FIRST_NAME+' '+row.FIRST_NAME == line.FIRST_NAME:
                match = True
            elif row.FIRST_NAME.replace('.', '') == line.FIRST_NAME[0]:
                match = True
            elif row.FIRST_NAME[0] == line.FIRST_NAME:
                match = True
            if match:
                new_dict = {
                    'NAME':row.NAME,
                    'ME':line.ME
                }
                dict_list_1.append(new_dict)
    return dict_list_1

def find_missing_2(missing_df, ppd):
    '''
    Matches unmatched names to ppd entries by first name
    '''
    dict_list_1 = []
    for row in missing_df.itertuples():
        print(row.LAST_NAME)
        match = False
        new_df = ppd[ppd.FIRST_NAME == row.FIRST_NAME]
        print(len(new_df))
        for line in new_df.itertuples():
            match = False
            if row.LAST_NAME in line.LAST_NAME:
                print(f'{row.NAME} matches {line.MAILING_NAME}')
                match = True
            elif len(line.LAST_NAME)>4 and line.LAST_NAME in row.LAST_NAME:
                print(f'{row.NAME} matches {line.MAILING_NAME}')
                match = True
            elif fuzz.ratio(row.LAST_NAME, line.LAST_NAME)>83:
                print(f'{row.NAME} matches {line.MAILING_NAME}')
                match = True
            elif row.MIDDLE_NAME == line.LAST_NAME:
                print(f'{row.NAME} matches {line.MAILING_NAME}')
                match = True
            elif row.MIDDLE_NAME+row.LAST_NAME == line.LAST_NAME:
                print(f'{row.NAME} matches {line.MAILING_NAME}')
                match = True
            elif row.SUFFIX.split(',')[0] == line.LAST_NAME:
                print(f'{row.NAME} matches {line.MAILING_NAME}')
                match = True
            if match:
                new_dict = {
                    'NAME':row.NAME,
                    'ME':line.ME
                }
                dict_list_1.append(new_dict)
    return dict_list_1

def clean_missing_matches(missing_match_df):
    '''
    Go through matched names and return only viable matches
    '''
    names = {}
    for row in missing_match_df.itertuples():
        keep = False
        if row.STATE == row.POLO_STATE:
            if (row.MD_DO_CODE == 1 and 'MD' in row.SUFFIX_y) or (row.MD_DO_CODE == 2 and 'DO' in row.SUFFIX_y):
                if fuzz.ratio(row.NAME.upper(), row.MAILING_NAME) > 72:
                    if fuzz.ratio(row.SPECIALTY.upper(), row.DESC_PRIM) > 80:
                        keep = True
                    elif row.DESC_PRIM in row.SPECIALTY.upper():
                        keep = True
                    elif row.SPECIALTY.upper() in row.DESC_PRIM:
                        keep = True
                    elif row.SPECIALTY.upper() in row.DESC_SEC:
                        keep = True
                    elif fuzz.ratio(row.SPECIALTY.upper(), row.DESC_SEC) > 80:
                        keep = True

                    mid_match = False
                    if row.MIDDLE_NAME_y != 'None':
                        print(row.MIDDLE_NAME_y)
                        print(row.MIDDLE_NAME_x)
                        if row.MIDDLE_NAME_x == row.MIDDLE_NAME_y:
                            mid_match = True
                        elif row.MIDDLE_NAME_y:
                            if row.MIDDLE_NAME_x[0] == row.MIDDLE_NAME_y[0]:
                                mid_match = True
                    if keep:
                        if row.NAME in names.keys():
                            if not names[row.NAME][1] and mid_match:
                                names[row.NAME][0] = row.ME
                                names[row.NAME][1] = mid_match
                        if row.NAME not in names.keys():
                            names[row.NAME] = [row.ME, mid_match, row.NAME]
    return names
