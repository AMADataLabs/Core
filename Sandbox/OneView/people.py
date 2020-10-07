'''Generate AAMC ID-ME key table'''
import os
import pandas as pd
import settings

def get_directors():
    '''Pull directors from personnel table and clean names'''
    personnel_file = os.environ.get('PROGRAM_PERSONNEL_FILE')
    personnel = pd.read_excel(personnel_file)
    directors = personnel[(personnel.pers_type == 'D')]
    directors = directors.fillna('None')
    directors['FIRST_NAME'] = [x.upper() for x in directors.pers_name_first]
    directors['LAST_NAME'] = [x.upper() for x in directors.pers_name_last]
    directors = directors[directors.aamc_id != 'None'].sort_values(
        ['survey_cycle']).drop_duplicates(['aamc_id'], keep='last')
    return directors

def get_ppd():
    '''Grab and transform ppd'''
    ppd_file = os.environ.get('PPD_FILE')
    ppd = pd.read_csv(ppd_file, low_memory=False)
    ppd['pers_deg1'] = ['MD' if x == 1 else 'DO' for x in ppd.MD_DO_CODE]
    return ppd

def initial_match(directors, ppd):
    '''Match directors and physicians'''
    all_match = pd.merge(ppd, directors, on=['FIRST_NAME', 'LAST_NAME'])
    pure_match = pd.merge(ppd, directors, on=[
        'FIRST_NAME', 'LAST_NAME']).drop_duplicates('aamc_id', keep=False)
    duplicate_matches = all_match[all_match.aamc_id.isin(pure_match.aamc_id) == False]
    duplicates = directors[directors.aamc_id.isin(duplicate_matches.aamc_id)]
    duplicate_matches = duplicate_matches.fillna('None')
    return (pure_match, duplicate_matches, duplicates)

def filter_out_duplicates(duplicates, duplicate_matches):
    '''Remove duplicate matches based on further filtering criteria'''
    matched_dict_list = []
    for row in duplicates.itertuples():
        new_df = duplicate_matches[duplicate_matches.aamc_id == row.aamc_id]
        if row.pers_deg1 != 'None' and row.pers_deg1 != 'MPH':
            new_df = new_df[new_df.pers_deg1_x == row.pers_deg1]
        if len(new_df) > 1 and row.pers_name_mid != 'None':
            if len(row.pers_name_mid) == 1:
                new_df['middle'] = [x[0] for x in new_df.MIDDLE_NAME]
                new_df = new_df[new_df.middle == row.pers_name_mid]
            else:
                new_df = new_df[new_df.MIDDLE_NAME == row.pers_name_mid.upper()]
        if len(new_df) == 1:
            matched_dict_list.append({'aamc_id':row.aamc_id, 'ME': list(new_df.ME)[0]})
    return matched_dict_list

def main():
    '''Create key table'''
    outfile = os.environ.get('OUTFILE')
    directors = get_directors()
    ppd = get_ppd()
    pure_match, duplicate_matches, duplicates = initial_match(directors, ppd)
    new_matches = filter_out_duplicates(duplicates, duplicate_matches)
    new_match = pd.DataFrame(new_matches)
    pd.concat([pure_match[['ME', 'aamc_id']], new_match]).to_csv(outfile, index=False)

if __name__ == "__main__":
    main()
