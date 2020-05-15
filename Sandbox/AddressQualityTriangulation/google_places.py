'''Google places functions'''
import os
import json
import requests
import settings
from datetime import date

def get_phone_parameters():
    '''Define values for google places phone lookup'''
    key = os.getenv('GPLACES_KEY')
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    fields = 'formatted_address,geometry,name,place_id,plus_code,types'
    inputtype = 'phonenumber'
    return (url, fields, inputtype, key)

def places_phone_lookup(phone):
    '''Call google places api on single number'''
    base_url, fields, inputtype, key = get_phone_parameters()
    list_of_dicts = []
    phone_formatted = '+1' + str(int(phone))
    parameters = {'fields': fields, 'inputtype': inputtype, 'key': key, 'input': phone_formatted}
    response = requests.get(base_url, params=parameters)
    if response.status_code == 200:
        results = response.json()
        for candidate in results['candidates']:
            person_dict = {}
            person_dict['Phone_Number'] = str(int(phone))
            person_dict['Name'] = candidate["name"]
            person_dict['Complete_Address'] = candidate['formatted_address']
            person_dict['Types'] = candidate['types']
            list_of_dicts.append(person_dict)
        if len(results['candidates']) == 0:
            person_dict = {}
            person_dict['Phone_Number'] = str(int(phone))
            person_dict['Name'] = 'None'
            person_dict['Complete_Address'] = 'None'
            person_dict['Types'] = 'None'
            list_of_dicts.append(person_dict)
    else:
        person_dict = {}
        person_dict['Phone_Number'] = str(int(phone))
        person_dict['Name'] = 'None'
        person_dict['Complete_Address'] = 'None'
        person_dict['Types'] = 'None'
    cleaned_address = clean_address(person_dict['Complete_Address'])
    person_dict['Address'] = cleaned_address['Address']
    person_dict['City'] = cleaned_address['City']
    person_dict['State'] = cleaned_address['State']
    person_dict['Zipcode'] = cleaned_address['Zipcode']
    list_of_dicts.append(person_dict)

    return (results, list_of_dicts)

def places_phone_list_lookup(phone_list):
    '''Call google places api on each number in phone list'''
    today = str(date.today())
    out_dir = os.getenv('GPLACES_DIR')
    all_results = []
    list_of_dicts = []
    for phone in phone_list:
        results, dicts = places_phone_lookup(phone)
        all_results.append(results)
        list_of_dicts += dicts
    with open(f'{out_dir}google_data_{today}.txt', 'w') as outfile:
        json.dump(all_results, outfile)
    return list_of_dicts

def clean_address(smushed_address):
    '''Split address into parts'''
    address_list = smushed_address.split(', ')
    if len(address_list) < 4 and len(address_list) > 1:
        address = 'None'
        city = address_list[0]
        state = address_list[1].split(' ')[0]
        zipcode = address_list[1].split(' ')[1]
    elif len(address_list) > 4:
        address = address_list[0] + ', ' + address_list[1]
        city = address_list[-3]
        state = address_list[-2].split(' ')[0]
        zipcode = address_list[-2].split(' ')[1]
    elif len(address_list) == 4:
        address = address_list[0]
        city = address_list[1]
        state = address_list[2].split(' ')[0]
        zipcode = address_list[2].split(' ')[1]
    else:
        address = 'None'
        city = 'None'
        state = 'None'
        zipcode = 'None'
    new_dict = {
        'Address': address,
        'City': city,
        'State': state,
        'Zipcode': zipcode,
        }
    return new_dict

def get_places_parameters():
    '''Define values for google places'''
    key = os.getenv('GPLACES_KEY')
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    fields = 'formatted_address,geometry,name,permanently_closed,place_id,plus_code,types'
    inputtype = 'textquery'
    return (url, fields, inputtype, key)

def places_lookup(address):
    '''Places lookup by text'''
    list_of_dicts = []
    base_url, fields, inputtype, key = get_places_parameters()
    parameters = {'fields': fields, 'inputtype':inputtype, 'key':key, 'input': address}
    response = requests.get(base_url, params=parameters)
    if response.status_code == 200:
        results = response.json()
        if len(results['candidates']) > 0:
            for candidate in results['candidates']:
                person_dict = {
                    'Name': candidate["name"],
                    'Address_Google': candidate['formatted_address'],
                    'Types': candidate['types'],
                    'Place_ID': candidate['place_id']
                }  
                list_of_dicts.append(person_dict)
        elif len(results['candidates']) == 0:  
            print(f'{address} not found')
    return (results, list_of_dicts)
