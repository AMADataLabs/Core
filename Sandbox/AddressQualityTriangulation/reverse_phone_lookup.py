'''This script can be run to call the GetPhoneInfo API on a list of phone numbers'''
import os
import json
import pandas as pd
import requests
import xmltodict
import settings
from datetime import date

#Reverse lookup a single phone number:
def reverse_lookup(phone_number):
    '''Lookup one phone number'''
    apikey = os.environ.get('GETPHONE_KEY')

    #Create an empty dictionary:
    info_dict = {}

    #Call api with given parameters and save xml as dictionary:
    base_url = "https://ws.serviceobjects.com/gppl2/api.svc/GetPhoneInfo"
    parameters = {'PhoneNumber': int(phone_number), 'LicenseKey': apikey}
    response = requests.get(base_url, params=parameters)
    results = xmltodict.parse(response.content)

    #Select phone info section of resulting dictionary:
    phone_results = results["PhoneInfoResponse"]["PhoneInfo"]

    #Save phone number:
    info_dict['Phone_Number'] = str(int(phone_number))

    #Save relevant values in results in smaller dictionary. Save null value if errors:
    try:
        info_dict["Name"] = phone_results["Contacts"]['Contact']["Name"]
    except:
        info_dict["Name"] = 'N/A'
    try:
        info_dict["Address"] = phone_results["Contacts"]['Contact']["Address"]
    except:
        info_dict["Address"] = 'None'
    try:
        info_dict["City"] = phone_results["Contacts"]['Contact']["City"]
    except:
        info_dict["City"] = 'N/A'
    try:
        info_dict["State"] = phone_results["Contacts"]['Contact']["State"]
    except:
        info_dict["State"] = 'N/A'
    try:
        info_dict["PhoneType"] = phone_results["Contacts"]['Contact']["PhoneType"]
    except:
        info_dict["PhoneType"] = 'N/A'
    try:
        info_dict["QualityScore"] = phone_results["Contacts"]['Contact']["QualityScore"]
    except:
        info_dict["QualityScore"] = 'N/A'
    try:
        info_dict["Date"] = phone_results["DateOfPorting"]
    except:
        info_dict["Date"] = 'none'
    try:
        info_dict["Notes"] = phone_results["NoteDescriptions"]
    except:
        info_dict["Notes"] = 'None'
    try:
        info_dict["Provider"] = phone_results['Provider']['Name']
    except:
        info_dict["Provider"] = 'N/A'
    try:
        info_dict["SICCode"] = phone_results["Contacts"]['Contact']['SICCode']
    except:
        info_dict["SICCode"] = 'None'
    try:
        info_dict["SICDesc"] = phone_results["Contacts"]['Contact']['SICDesc']
    except:
        info_dict["SICDesc"] = 'None'

    #Return resulting dictionary and full dictionary:
    return(info_dict, results)


#Test all number in a dataframe:
def test_numbers(phone_list):
    '''Many numbers'''
    today = str(date.today())
    out_dir = os.getenv('GETPHONE_DIR')
    #Create two empty lists:
    results_dict_list = []
    all_results = []

    #Iterate through dataframe and call reverse_lookup on each number:
    for phone in phone_list:
        new_dict = {}
        try:
            new_dict, phone_results = reverse_lookup(phone)
            results_dict_list.append(new_dict)
            all_results.append(phone_results)
        except:
            pass

    #Save lists of dictionaries as dataframes:
    new_df = pd.DataFrame(results_dict_list)
    with open(f'{out_dir}getphone_data_{today}.txt', 'w') as outfile:
        json.dump(all_results, outfile)
    #Return dataframes:
    return(new_df)

#Export results to files:
def export_results(phone_csv, xml_location, df_location, phone_column):
    '''Run and save results'''
    #Create dataframe from csv:
    phone_df = pd.DataFrame(phone_csv)
    phones = list(phone_df[phone_column])

    #Call test_numbers on dataframe:
    fun_massive_list, final_df = test_numbers(phones)

    #Export results:
    final_df.to_csv(df_location)
    try:
        with open(f'{xml_location}_data.txt', 'w') as outfile:
            json.dump(fun_massive_list, outfile)
    except:
        pass

    print("Files saved")

# if __name__ == "__main__":
#     export_results()
