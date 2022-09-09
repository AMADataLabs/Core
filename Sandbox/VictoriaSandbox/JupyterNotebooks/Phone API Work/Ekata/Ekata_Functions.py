import pandas as pd 
from ekata_utility import key

def reverse_lookup(phone_number, key):
    info_dict = {}
    base_url = 'https://proapi.whitepages.com/3.1/phone?'
    parameters = {'phone':phone_number, 'api_key': key}
    response =  requests.get(base_url, params=parameters)
    results = response.json()
    info_dict['OFFICE_TELEPHONE'] = phone_number
    try:
        info_dict["Name"] = results['belongs_to']['name']
    except:
        info_dict["Name"] = 'N/A'
    try:
        info_dict["Address"] = results['current_addresses'][0]['street_line_1']
    except:
        info_dict["Address"] = 'N/A'
    try:
        info_dict["City"] = results['current_addresses'][0]['city']
    except:
        info_dict["City"] = 'N/A'
    try:
        info_dict["State"] = results['current_addresses'][0]['state_code']
    except:
        info_dict["State"] = 'N/A'
    try: 
        info_dict["Zipcode"] = results['current_addresses'][0]['postal_code']
    except:
        info_dict["Zipcode"] = 'N/A'
    try:
        info_dict["PhoneType"] = results['belongs_to']['type']
    except:
        info_dict["PhoneType"] = 'N/A'
    try:
        info_dict["Valid"] = results['is_valid']
    except:
        info_dict["Valid"] = 'N/A'
    try:
        info_dict["Date"] = results['current_addresses'][0]['link_to_person_start_date']
    except:
        info_dict["Date"] = 'N/A'
    try:
        info_dict["LineType"] = results['line_type']
    except:
        info_dict["LineType"] = 'N/A'
    try:
        info_dict["Carrier"] = results['carrier']
    except:
        info_dict["Carrier"] = 'N/A'
    try:
        info_dict["Commercial"] = results['is_commercial']
    except:
        info_dict["Commercial"] ='N/A'
    try:
        info_dict["Industry"] = results['belongs_to']['industry'][0]
    except:
        info_dict["Industry"] = 'N/A'
    try:
        info_dict["AlternatePhone"] = results['alternate_phones'][0]['phone_number']
    except:
        info_dict["AlternatePhone"] = 'N/A'
    try:
        info_dict['Error'] = results['error']
    except:
        info_dict['Error'] = 'None'
    return(info_dict, results)

def test_numbers(dataframe, key):
    results_dict_list = []
    fun_massive_list = []
    count = 0
    for row in dataframe.itertuples():
        count = count +1
        new_dict = {}
        phone = str(row.OFFICE_TELEPHONE)[0:10]
        try:
            new_dict, phone_results = reverse_lookup(phone, key)
            results_dict_list.append(new_dict)
            fun_massive_list.append(phone_results)
        except:
            pass
        print(count)
    new_df = pd.DataFrame(results_dict_list)
    return(fun_massive_list, new_df)

def analyze_numbers(dataframe):
    
    name_match = 0
    healthy = 0
    address_match = 0
    city_match = 0
    zipcode_match = 0
    commercial = 0
    no_address = 0
    no_date = 0
    industry = 0
    landline = 0
    business = 0

    for row in dataframe.itertuples():
        address_matched = False
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.Name_Ekata).lower():
            name_match +=1
        if is_healthy(row.Name_Ekata) == True:
            healthy += 1
        if str(row.OFFICE_ADDRESS_LINE_2).lower() in str(row.Address_Ekata).lower():
            address_match +=1
        if row.OFFICE_ADDRESS_ZIPCODE == row.Zipcode_Ekata:
            zipcode_match += 1
        if str(row.OFFICE_ADDRESS_CITY).lower() in str(row.City_Ekata).lower():
            city_match += 1
        if row.Commercial == True:
            commercial += 1
        if 'Ambulatory Health Care Services' in str(row.Industry):
            industry += 1
        if row.Industry == 'Nursing and Residential Care Facilities':
            industry += 1
        if row.Industry == 'Hospitals':
            industry += 1
        if row.LineType == 'Landline':
            landline += 1

        if row.Address_Ekata == 'None':
            no_address += 1
        if row.Date_Ekata == 'None':
            no_date += 1
        if row.PhoneType_Ekata == 'Business':
            business += 1


    new_dict = {
        'Address Matches': address_match,
        'City Matches': city_match,
        'Exact Name Matches': name_match,
        'Relevant Names': healthy,
        'No Address': no_address,
        'No Date': no_date,
        'Business Phone': business,
        'Commercial': commercial,
        'Correct Industry': industry,
        'Landline': landline
        }
        
    return(new_dict)

def is_healthy(name):
    med_words = ['cancer', 'cardiology', 'neurology', 'family care', 'pulmonary', 'anesthesia', 'orthope', 'urgent care', 'allergy', 'kidney', 'surgery', 'hosp', 'mri', 'throat', 'dentist', 'med', 'clinic', 'health', 'gastroenter','anesthesiologist','patient','physician','surgeon','doctor','hospital', 'md', 'medical', 'pediatrics', 'm.d.']
    healthy = False
    for word in med_words:
        if word in str(name).lower():
            healthy = True   
    return(healthy)