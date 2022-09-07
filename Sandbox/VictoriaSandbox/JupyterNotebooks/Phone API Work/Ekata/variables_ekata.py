def is_healthy(name):
    med_words = ['cancer', 'cardiology', 'neurology', 'family care', 'pulmonary', 'anesthesia', 'orthope', 'urgent care', 'allergy', 'kidney', 'surgery', 'hosp', 'mri', 'throat', 'dentist', 'med', 'clinic', 'health', 'gastroenter','anesthesiologist','patient','physician','surgeon','doctor','hospital', 'md', 'medical', 'pediatrics', 'm.d.']
    healthy = False
    for word in med_words:
        if word in str(name).lower():
            healthy = True   
    return(healthy)

def variable_breakdown(dataframe):
    
    LIST_OF_DICTS = []
    
    
    for row in dataframe.itertuples():

        address_match = 0
        no_alternate_phone = 0
        ambulatory = 0
        fixed_voip = 0
        non_fixed_voip = 0
        hospitals = 0
        landline = 0
        mobile = 0
        no_industry = 0
        no_phonetype = 0
        nursing = 0
        personal = 0
        city_match = 0
        zipcode_match = 0
        state_match = 0
        health = 0
        no_address = 0
        no_date = 0
        business = 0
        first_name_match = 0
        last_name_match = 0 
        workplace_match = 0
        

        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.Name).lower():
            last_name_match +=1
        if is_healthy(row.Name) == True:
            health = 1
        if str(row.OFFICE_ADDRESS_LINE_2).lower() in str(row.Address).lower():
            address_match =1
        if row.OFFICE_ADDRESS_ZIPCODE == row.Zipcode:
            zipcode_match = 1
        if str(row.OFFICE_ADDRESS_CITY).lower() in str(row.City).lower():
            city_match = 1
        if str(row.OFFICE_ADDRESS_STATE).lower() in str(row.State).lower():
            state_match = 1
        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.Name).lower():
            workplace_match = 1
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.Name).lower():
            first_name_match =1

        if row.Address == 'None':
            no_address = 1
        if row.Date == 'None':
            no_date = 1
        if row.Industry == 'None':
            no_industry = 1
        if row.PhoneType == 'None':
            no_phonetype = 1
        if row.PhoneType == 'Business':
            business = 1
        if row.PhoneType == 'Person':
            personal = 1

        if row.AlternatePhone == 'None':
            no_alternate_phone = 0

        if 'Ambulatory' in str(row.Industry):
            ambulatory = 1
        if 'Nursing' in str(row.Industry):
            nursing = 1
        if 'Hospitals' in str(row.Industry):
            hospitals = 1

        if row.LineType == 'Landline':
            landline = 1
        if row.LineType == 'FixedVOIP':
            fixed_voip = 1
        if row.LineType == 'NonFixedVOIP':
            non_fixed_voip = 1
        if row.LineType == 'Mobile':
            mobile = 1

        new_dict = {
            'OFFICE_TELEPHONE': row.OFFICE_TELEPHONE,
            'Address Match': address_match,
            'City Match': city_match,
            'ZipCode Match': zipcode_match,
            'State Match': state_match,
            'No Address': no_address,
            'No Date': no_date,
            'No PhoneType': no_phonetype,
            'No Industry': no_industry,
            'Relevant Name': health,
            'Business Phone': business,
            'Personal Phone': personal,
            'No Alternate Phone': no_alternate_phone,
            'Ambulatory Industry':ambulatory,
            'Hospital Industry': hospitals,
            'Nursing Industry':nursing,
            'Fixed VOIP': fixed_voip,
            'Non Fixed Voip': non_fixed_voip, 
            'Landline': landline,
            'Mobile': mobile,
            'First Name Match':first_name_match,
            'Last Name Match':last_name_match,
            'Workplace Match': workplace_match
            }

        LIST_OF_DICTS.append(new_dict)

    return(LIST_OF_DICTS)