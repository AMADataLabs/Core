'''
This script makes Google Places API calls for phone numbers in a csv and outputs a csv of results
'''
import requests
import pandas as pd
import json
from auth import key
from datetime import date
from tkinter import filedialog

def get_filename():
    '''
    Gets filename
    '''
    choice = input('Enter filename or "choose" to choose in directory:  ')
    if choice == 'choose':
        csv_file = filedialog.askopenfilename(initialdir = "C:\\Users\\vigrose\\Jupyter Notebooks\\Phone API Work\\GetPhoneInfo\\Data\\",
                                         title = "Choose the physician contact data file to use...")
    else:
        csv_file = choice
    return csv_file


def get_phone_list(contact_df):
    '''
    Finds phone list in csv
    '''
    #Check for 'phone' in column names
    phone = False
    for col in contact_df.columns:   
        if 'phone' in col.lower():
            if phone == True:
                print('Warning: Multiple columns contain phone numbers')
                this = input(f'Choose [1] for {col} [2] for {phone_col}:  ')
                if this == 1:
                    phone_col = col
            else: 
                phone = True
                phone_col = col
    if phone:
        phone_list = list(contact_df[phone_col])
    else:
        print('No phone number column found')
        return []
    return phone_list

def google_phone_call(phone_list):
    '''
    Calls api on each phone number in list
    '''
    proceed = 'Y'
    if len(phone_list) > 500:
        print('Amount of expected API calls is greater than 500. Do you wish to proceed?')
        proceed = input('Y/N ')
    if proceed == 'N':
        print('Terminating...')
        return
    all_results =[]
    #Set parameters
    base_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    fields = 'formatted_address,geometry,name,place_id,plus_code,types'
    inputtype='phonenumber'
    #Loop through list
    for number in phone_list:
        print("")
        print('----------------------')
        phone = '+1' + str(int(number))
        parameters = {'fields': fields, 'inputtype':inputtype, 'key':key,'input': phone}
        response =  requests.get(base_url, params=parameters)
        if response.status_code == 200:
            results = response.json()
            all_results.append(results)
            if len(results['candidates'])>0:
                for candidate in results['candidates']:
                    index = results['candidates'].index(candidate)
                    print(f'{index + 1}. {candidate["name"]}')
        else:
            print(f'{phone} not found')
    return all_results

def create_df(google_results, phones):
    '''
    Creates dataframe from google results
    '''
    dict_list =[]
    index= 0
    for result in google_results:
        phone_number = phones[index]
        if result['status'] == 'OK':
            for candidate in result['candidates']:
                name = candidate['name']
                address_list = candidate['formatted_address'].split(', ')
                address_list = list(dict.fromkeys(address_list))
                if len(address_list)<4:
                    address = 'None'
                    city = address_list[0]
                    state = address_list[1].split(' ')[0]
                    try:
                        zipcode = address_list[1].split(' ')[1]
                    except:
                        zipcode = 'None'
                elif len(address_list)>4:
                    address = address_list[0] + ', ' + address_list[1]
                    city = address_list[-3]
                    state = address_list[-2].split(' ')[0]
                    zipcode = address_list[-2].split(' ')[1]
                else:
                    address = address_list[0]
                    city = address_list[1]
                    state = address_list[2].split(' ')[0]
                    zipcode = address_list[2].split(' ')[1]
                types = candidate['types']
                new_dict = {
                    'PHONE:': phone_number,
                    'NAME': name,
                    'ADDRESS': address,
                    'CITY': city,
                    'STATE': state,
                    'ZIPCODE': zipcode,
                    'TYPES':types,
                    'COMPLETE_ADDRESS': candidate['formatted_address']
                }
                dict_list.append(new_dict)
        else:
            new_dict = {
                    'PHONE:': phone_number,
                    'NAME':'None',
                    'ADDRESS':'None',
                    'CITY':'None',
                    'STATE':'None',
                    'ZIPCODE':'None',
                    'TYPES':'None',
                    'COMPLETE_ADDRESS':'None'
                }
            dict_list.append(new_dict) 
        index += 1
    result_df = pd.DataFrame(dict_list)
    return result_df
def save_csv(google_results, phones):
    '''
    Saves dataframe of data as csv
    ''' 
    result_df = create_df(google_results, phones)
    result_directory = "C:\\Users\\vigrose\\Jupyter Notebooks\\Phone API Work\\GetPhoneInfo\\Data\\"
    print(f'Saving results to {result_directory}')
    today = str(date.today())
    result_df.to_csv(result_directory +  'Google_Results_' + today + '.csv', index = False)

def save_text(google_results):
    '''
    Saves all results as text file
    '''
    print(f'Saving results to {result_directory}')
    today = str(date.today())
    result_directory = "C:\\Users\\vigrose\\Jupyter Notebooks\\Phone API Work\\GetPhoneInfo\\Data\\"
    text_filename = result_directory +  'Google_Results_Dump_' + today + '.txt'
    with open(text_filename, 'w') as outfile:
            json.dump(google_results, outfile)

def google_places():
    '''
    Runs above functions to call google places api on phones and save results
    '''
    print('Running...')
    file_name = get_filename()
    print('Reading file...')
    contact_df = pd.read_csv(file_name)
    phones = get_phone_list(contact_df)
    print(f'Making {len(phones)} API calls..')
    if len(phones) > 0:
        results = google_phone_call(phones)
        try: 
            save_csv(results, phones)
            save_text(results)
        except:
            print('Issues saving to dataframe')
            save_text(results)
    else:
        print('Unable to complete. Check original file')
        return

if __name__ == "__main__":
    google_places()