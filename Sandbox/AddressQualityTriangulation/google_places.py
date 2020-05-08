'''Google places functions'''
import requests
import pandas as pd
import settings
import os
import json

def get_places_parameters():
    '''Define values for google places'''
    key = os.getenv('GPLACES_KEY')
    base_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
    fields = 'formatted_address,geometry,name,place_id,plus_code,types'
    inputtype='phonenumber'
    return (url, fields, inputtype, key)

def places_lookup(phone_list):
    '''Call google places api on each number in phone list'''
    base_url, fields, inputype, key = get_places_parameters()
    all_results =[]
    list_of_dicts = []
    for phone in phone_list:
        phone = '+1' + str(phone)
        parameters = {'fields': fields, 'inputtype':inputtype, 'key':key,'input': phone}
        response =  requests.get(base_url, params=parameters)
        if response.status_code == 200:
            results = response.json()
            all_results.append(results)
            for candidate in results['candidates']:
                    person_dict = {}
                    person_dict['TELEPHONE_NUMBER'] = phone
                    person_dict['Name'] = candidate["name"]
                    person_dict['Address'] = candidate['formatted_address']
                    person_dict['Types'] = candidate['types']
                    list_of_dicts.append(person_dict)
            if len(results['candidates'])==0:   
                person_dict = {}
                person_dict['TELEPHONE_NUMBER'] = phone
                person_dict['Name'] = 'None'
                person_dict['Address'] = 'None'
                person_dict['Types'] = 'None'
                list_of_dicts.append(person_dict)   
        else:
            person_dict = {}
            person_dict['TELEPHONE_NUMBER'] = phone
            person_dict['Name'] = 'None'
            person_dict['Address'] = 'None'
            person_dict['Types'] = 'None'
            list_of_dicts.append(person_dict) 
    return (all_results, list_of_dicts)

def clean_address(list_of_dicts):
    '''Split address into parts'''
    dict_list =[]
    for thing in x:
        address_list = thing['Address'].split(', ')
        if len(address_list)<4 and len(address_list)>1:
            address = 'None'
            city = address_list[0]
            state = address_list[1].split(' ')[0]
            zipcode = address_list[1].split(' ')[1]
        elif len(address_list)>4:
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
            city ='None'
            state = 'None'
            zipcode = 'None'
        new_dict = {
                    'NAME': thing['Name'],
                    'ADDRESS': address,
                    'CITY': city,
                    'STATE': state,
                    'ZIPCODE': zipcode,
                    'COMPLETE_ADDRESS': thing['Address']
            }
        dict_list.append(new_dict)
    return dict_list