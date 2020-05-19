'''Office Address Triangulation'''
import os
import pandas as pd
import settings
import get_insurance_data
from google_places import places_phone_list_lookup
import match
from reverse_phone_lookup import test_numbers
import score

def get_newest(env_path, text):
    '''Grabs newest data'''
    directory = os.getenv(env_path)
    files = os.listdir(directory)
    paths = [os.path.join(directory, basename) for basename in files if text in basename]
    filename = max(paths, key=os.path.getctime)
    return pd.read_csv(filename)

def get_data(get_new_insurance):
    '''Get data'''
    dhc = get_newest('DHC_DIR', 'DHC')
    if get_new_insurance != 'NO':
        insurance = get_insurance_data.get_insurance()
    else:
        insurance = get_newest('AMAIA_DIR', 'Insurance')
    return(dhc, insurance)

def read_input(input_file):
    '''
    Read and slightly clean input file
    Check if necessary columns are present
    '''
    addresses = pd.read_csv(input_file)
    addresses.columns = [c.replace(' ', '_').title() for c in addresses.columns.values]
    cols = ['Phone', 'Address_1', 'Address_3']
    necessary_columns = ['Address_2', 'City', 'State', 'Zipcode', 'Me']
    for col in cols:
        if col not in addresses.columns:
            addresses[col] = 'None'
    addresses = addresses.fillna('None')
    addresses['Phone'] = addresses['Phone'].apply(lambda x: str(x).replace('.', ''.replace('-', '')))
    addresses['Address_2'] = addresses['Address']
    for col in necessary_columns:
        if col not in addresses.columns:
            print(f'{col} is missing from input')
            return []
        if len(addresses[addresses[col] == 'None']) > 0:
            print(f'At least one row is missing {col}')
            return []
    addresses = addresses[cols+necessary_columns]
    addresses = addresses.rename(columns={'Me':'ME'})
    return addresses

def merge_address_data(dhc, new_add, insurance):
    '''lol'''
    try:
        new_add = pd.merge(dhc, new_add, on='ME', how='right', suffixes=['_DHC', '_New'])
    except TypeError:
        print('Input format is incorrect')
        return
    new_add = pd.merge(insurance, new_add, on='ME', how='right')
    return new_add

def create_master_phones(full_table):
    '''Get phone list from matching dhc address'''
    phone_list = []
    for row in full_table.itertuples():
        if row.Phone != 'None':
            phone_list.append(str(int(row.Phone)))
        elif row.DHC_Address_Match:
            phone_list.append(str(int(row.Phone_Number)))
        else:
            phone_list.append('None')
    full_table['Phone_Complete'] = phone_list
    matches = full_table[full_table.Phone_Complete != 'None']
    return (full_table, list(matches.Phone_Complete.unique()))

def phone_call(phone_list):
    '''Make reverse phone lookups with new numbers'''
    google_addresses = places_phone_list_lookup(phone_list)
    google = pd.DataFrame(google_addresses)
    getphone = test_numbers(phone_list)
    phone_results = pd.merge(google, getphone, on='Phone_Number', suffixes=['_Google', '_GetPhone'])
    return phone_results

def main():
    '''lalalla'''
    input_csv = input('Enter input file location, leave blank to use dotenv ') or os.getenv('INPUT')
    get_new_insurance = os.getenv('NEW_INSURANCE')
    print('Getting data...')
    out_dir = os.getenv('OUT_DIR')
    dhc, insurance = get_data(get_new_insurance)
    new_addresses = read_input(input_csv)
    print("Merging...")
    new_addresses = merge_address_data(dhc, new_addresses, insurance)
    new_addresses, master_phone_list = create_master_phones(new_addresses)
    new_addresses.to_csv(f'{out_dir}/Raw_Triangulation_Data.csv', index=False)
    print('API Calling...')
    reverse_phone_results = phone_call(master_phone_list)
    new_addresses.to_csv(f'{out_dir}/Raw_Triangulation_Data.csv', index=False)
    new_addresses = pd.merge(reverse_phone_results, new_addresses, left_on='Phone_Number', right_on='Phone_Complete', how='right', suffixes = ['_Reverse',''])
    print('Matching...')
    #Check address matches
    matched = match.find_address_matches(new_addresses)
    #Check address phone matches
    matched = match.find_phone_address_matches(matched)
    #Score matches
    add_score_list = score.score_addresses(matched)
    add_scored = pd.DataFrame(add_score_list)
    phone_score_list = score.score_phone_address_links(matched)
    phone_scored = pd.DataFrame(phone_score_list)
    scored = pd.merge(phone_scored, add_scored, on=['ME', 'Address_2'])
    scored = scored.sort_values('Address_2_Match_Rate', ascending=False)
    scored = scored.drop_duplicates(['ME', 'Address_2', 'Master_Phone'])
    #Save results
    matched.to_csv(f'{out_dir}/Matched_Data.csv', index=False)
    scored.to_csv(f'{out_dir}/Triangulation_Report.csv', index=False)

if __name__ == "__main__":
    main()
