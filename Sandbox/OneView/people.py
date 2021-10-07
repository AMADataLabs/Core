'''Generate AAMC ID-ME key table'''
import os
import pandas as pd
import settings
import logging

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

def get_directors():
    personnel_file = os.environ.get('PROGRAM_PERSONNEL_FILE')
    directors = pd.read_csv(personnel_file)
    directors = directors.fillna('None')  
    directors['first_name'] = [x.upper().strip() for x in directors.first_name]
    directors['last_name'] = [x.upper().strip() for x in directors.last_name]

    return directors

def find_unique(directors):
    identifying_fields = ['last_name','first_name','middle_name','degree_1','degree_2','degree_3']
    unique_directors = directors.drop_duplicates(identifying_fields).sort_values('last_name')
    unique_directors = unique_directors[identifying_fields]
    unique_directors['person_id'] = list(range(len(unique_directors)))
    directors = pd.merge(directors, unique_directors, on = identifying_fields)
    
    return directors, unique_directors

def get_physicians():
    physician_file = os.environ.get('PPD_FILE')
    physicians = pd.read_csv(physician_file, low_memory=False)
    physicians['degree_1'] = ['MD' if x == 1 else 'DO' for x in physicians.degree_type]
    physicians['first_name'] = [str(x).upper().strip() for x in physicians.first_name]
    physicians['last_name'] = [str(x).upper().strip() for x in physicians.last_name]

    return physicians

def get_matches(directors, ppd):
    all_match = pd.merge(ppd, directors, on=['first_name', 'last_name'], suffixes=('_physician', '_residency'))
    pure_match = pd.merge(ppd, directors, on=[
        'first_name', 'last_name'], suffixes=('_physician', '_residency')).drop_duplicates('person_id', keep=False)
    
    return all_match, pure_match

def create_duplicate_matches(all_match, pure_match, directors):
    duplicate_matches = all_match[~all_match.person_id.isin(pure_match.person_id)]
    duplicates = directors[directors.person_id.isin(duplicate_matches.person_id)]
    duplicate_matches = duplicate_matches.fillna('None')

    return duplicate_matches, duplicates

def filter_out_duplicates(duplicates, duplicate_matches):
    matched_dict_list = []

    for row in duplicates.itertuples():
        new_df = merge_filtered_dataframe(row, duplicate_matches)
        if len(new_df) == 1:
            matched_dict_list.append({'person_id':row.person_id, 'medical_education_number': list(new_df.medical_education_number)[0]})

    return pd.DataFrame(matched_dict_list)

def merge_filtered_dataframe(row, duplicate_matches):
    new_df = duplicate_matches[duplicate_matches.person_id == row.person_id]

    if row.degree_1 != 'None' and row.degree_1 != 'MPH':
        new_df = new_df[new_df.degree_1_physician == row.degree_1]

    if len(new_df) > 1 and row.middle_name != 'None':
        if len(row.middle_name) == 1:
            new_df['middle'] = [x[0] for x in new_df.middle_name_physician]
            new_df = new_df[new_df.middle == row.middle_name]
        else:
            new_df = new_df[new_df.middle_name_physician == row.middle_name.upper()]

    return new_df

def get_all_links(pure_match, new_match, directors):
    linking_data = pd.concat([pure_match[['medical_education_number', 'person_id']], new_match])

    return pd.merge(linking_data, directors, on='person_id')[['medical_education_number','program']]

def main():
    outfile = os.environ.get('OUTFILE')
    LOGGER.info('Getting directors...')
    directors = get_directors()
    LOGGER.info('Getting ppd...')
    physicians = get_physicians()
    LOGGER.info('Matching...')

    directors, unique_directors = find_unique(directors)

    all_match, pure_match = get_matches(unique_directors, physicians)
    duplicate_matches, duplicates = create_duplicate_matches(all_match, pure_match, directors)
    new_match = filter_out_duplicates(duplicates, duplicate_matches)
    physician_directors = get_all_links(pure_match, new_match, directors)
    physician_directors.to_csv(outfile, index=False)

if __name__ == "__main__":
    main()


