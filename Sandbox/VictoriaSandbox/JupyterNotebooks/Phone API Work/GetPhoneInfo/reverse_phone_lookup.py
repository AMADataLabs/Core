'''This script can be run from the command line to call the GetPhoneInfo API on a csv containing a list of phone numbers'''

#Reverse lookup a single phone number:
def reverse_lookup(phone_number, column_name, apikey):

    #Create an empty dictionary:
    info_dict = {}

    #Call api with given parameters and save xml as dictionary:
    base_url = "https://trial.serviceobjects.com/GPPL2/api.svc/GetPhoneInfo"
    parameters = {'PhoneNumber': phone_number, 'LicenseKey': apikey}
    response =  requests.get(base_url, params=parameters)
    results = xmltodict.parse(response.content)

    #Select phone info section of resulting dictionary:
    phone_results = results["PhoneInfoResponse"]["PhoneInfo"]

    #Save phone number:
    info_dict[column_name] = phone_number

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

    #Return resulting dictionary and full dictionary:
    return(info_dict, results)


#Test all number in a dataframe:
def test_numbers(dataframe, column_name, apikey):

    #Create two empty lists:
    results_dict_list = []
    fun_massive_list = []

    #Iterate through dataframe and call reverse_lookup on each number:
    for row in dataframe.itertuples():
        new_dict = {}
        phone = row.column_name
        try:
            new_dict, phone_results = reverse_lookup(phone, column_name, apikey)
            results_dict_list.append(new_dict)
            fun_massive_list.append(phone_results)
        except:
            pass

    #Save lists of dictionaries as dataframes:
    new_df = pd.DataFrame(results_dict_list)
    final_df = pd.merge(new_df, dataframe, on = column_name)

    #Return dataframes:
    return(fun_massive_list, final_df)

#Export results to files:
def export_results():

    #Input variables from command line:
    key = input("Input API key:  ")
    phone_csv = input("Input path to csv:  ")
    column_header = input("Input phone numbers column headers (Default is 'Number')") or 'Number'
    xml_location = input("Input xml filepath  ") or 'fun_massive_list.txt'
    df_location = input("Input dataframe location  ") or 'reverse_lookup.csv'

    #Import dependencies
    import pandas as pd
    import requests
    import xmltodict
    import matplotlib.pyplot as plt

    #Create dataframe from csv:
    phone_df = pd.DataFrame(phone_csv)

    #Call test_numbers on dataframe:
    fun_massive_list, final_df = test_numbers(phone_df, column_header, key)

    #Export results:
    final_df.to_csv(df_location)

    print("Files saved")

if __name__ == "__main__":
    export_results()