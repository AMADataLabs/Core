def is_healthy(name):
    med_words = ['oncology','primary care','radiology','pathology','pathologists','glaucoma','cancer', 'cardiology', 'neurology', 'family care', 'pulmonary', 'anesthesia', 'orthope', 'urgent care', 'allergy', 'kidney', 'surgery', 'hosp', 'mri', 'throat', 'dentist', 'med', 'clinic', 'health', 'gastroenter','anesthesiologist','patient','physician','surgeon','doctor','hospital', 'md', 'medical', 'pediatrics', 'm.d.']
    healthy = False
    for word in med_words:
        if word in str(name).lower():
            healthy = True   
    return(healthy)

def variable_breakdown(dataframe):
    
    LIST_OF_DICTS = []
    
    
    for row in dataframe.itertuples():

        address_match = 0
        city_match = 0
        zipcode_match = 0
        health = 0
        mail = 0
        connect = 0
        port = 0
        novalid = 0
        unknown = 0
        disconnected = 0
        voip = 0
        wireless = 0
        address = 0
        date = 0
        business = 0
        residential = 0
        low = 0
        high = 0
        med = 0
        first_name_match = 0
        last_name_match = 0 
        workplace_match = 0
        state_match = 0

        if str(row.ContactAddressOut) in str(row.OFFICE_ADDRESS_LINE_2) or str(row.OFFICE_ADDRESS_LINE_2) in str(row.ContactAddressOut):
            address_match += 1
        if str(row.OFFICE_ADDRESS_CITY) in str(row.ContactCityOut):
            city_match += 1
        if clean_zipcode(row.OFFICE_ADDRESS_ZIP) == clean_zipcode(row.ContactZipOut):
            zipcode_match += 1      
        if row.ContactStateOut == row.OFFICE_ADDRESS_STATE:
            state_match += 1

        
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.ContactNameOut).lower():
            last_name_match =1
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.ContactNameOut).lower():
            first_name_match =1

        if is_healthy(row.ContactNameOut) == True:  
            health = 1

        if 'IsMailable' in str(row.NoteDescriptions):
            mail = 1
        if 'IsConnected' in str(row.NoteDescriptions):
            connect = 1
        if 'IsPorted' in str(row.NoteDescriptions):
            port = 1
        if 'NotValid' in str(row.NoteDescriptions):
            novalid = 1
        if 'IsUnknownContact' in str(row.NoteDescriptions):
            unknown = 1
        if 'IsPossibleDisconnected' in str(row.NoteDescriptions):
            disconnected = 1
        if 'IsPossiblePortableVOIP' in str(row.NoteDescriptions):
            voip = 1
        if 'IsWireless' in str(row.NoteDescriptions):
            wireless = 1

        if row.ContactAddressOut == 'None':
            address = 1
        if row.DateOfPorting == 'None':
            date = 1
        if row.ContactPhoneType == 'BUSINESS':
            business = 1
        if row.ContactPhoneType == 'RESIDENTIAL':
            residential = 1
        if row.ContactQualityScore == 'LOW':
            low = 1
        if row.ContactQualityScore == 'HIGH':
            high = 1
        if row.ContactQualityScore == 'MED':
            med = 1

        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.ContactNameOut).lower():
            workplace_match = 1

        new_dict = {
            'OFFICE_TELEPHONE': row.OFFICE_TELEPHONE,
            'Address Match': address_match,
            'City Match': city_match,
            'ZipCode Match': zipcode_match,
            'State Match': state_match,
            'No Address': address,
            'No Date': date,
            'Relevant Name': health,
            'Business Phone': business,
            'Residential Phone': residential,
            'Low Quality': low,
            'Medium Quality': med,
            'High Quality': high,
            'Mailable': mail,
            'Connected': connect,
            'Ported': port,
            'Unknown Contact': unknown,
            'Possibly Disconnected': disconnected,
            'Possibly Portable VOIP': voip,
            'First Name Match':first_name_match,
            'Last Name Match':last_name_match,
            'Workplace Match': workplace_match
            }

        LIST_OF_DICTS.append(new_dict)

    return(LIST_OF_DICTS)

def analyze_numbers(dataframe):
    
    
    address_match = 0
    city_match = 0
    zipcode_match = 0
    healthcount = 0
    mailcount = 0
    connectcount = 0
    portcount = 0
    novalidcount = 0
    unknowncount = 0
    disconnectedcount = 0
    voipcount = 0
    wirelesscount = 0
    no_address_count = 0
    no_date_count = 0
    business_count = 0
    residential_count = 0
    low_count = 0
    high_count = 0
    med_count = 0
    first_name_match = 0
    last_name_match = 0 
    workplace_match = 0
    state_match = 0
    no_name = 0
        


    for row in dataframe.itertuples():
        if str(row.ContactAddressOut) in str(row.OFFICE_ADDRESS_LINE_2) or str(row.OFFICE_ADDRESS_LINE_2) in str(row.ContactAddressOut):
            address_match += 1
        if str(row.OFFICE_ADDRESS_CITY) in str(row.ContactCityOut):
            city_match += 1
        if clean_zipcode(row.OFFICE_ADDRESS_ZIP) == clean_zipcode(row.ContactZipOut):
            zipcode_match += 1
        
        if row.ContactStateOut == row.OFFICE_ADDRESS_STATE:
            state_match += 1
        
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.ContactNameOut).lower():
            last_name_match +=1
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.ContactNameOut).lower():
            first_name_match +=1
        
        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.ContactNameOut).lower():
            workplace_match += 1

        if is_healthy(row.ContactNameOut)==True:    
            healthcount += 1

        if 'IsMailable' in str(row.NoteDescriptions):
            mailcount += 1
        if 'IsConnected' in str(row.NoteDescriptions):
            connectcount += 1
        if 'IsPorted' in str(row.NoteDescriptions):
            portcount += 1
        if 'NotValid' in str(row.NoteDescriptions):
            novalidcount += 1
        if 'IsUnknownContact' in str(row.NoteDescriptions):
            unknowncount += 1
        if 'IsPossibleDisconnected' in str(row.NoteDescriptions):
            disconnectedcount += 1
        if 'IsPossiblePortableVOIP' in str(row.NoteDescriptions):
            voipcount += 1
        if 'IsWireless' in str(row.NoteDescriptions):
            wirelesscount += 1

        if row.ContactAddressOut == 'None':
            no_address_count += 1
        if row.DateOfPorting == 'None':
            no_date_count += 1
        if row.ContactPhoneType == 'BUSINESS':
            business_count += 1
        if row.ContactPhoneType == 'RESIDENTIAL':
            residential_count += 1
        if row.ContactQualityScore == 'LOW':
            low_count += 1
        if row.ContactQualityScore == 'HIGH':
            high_count += 1
        if row.ContactQualityScore == 'MED':
            med_count += 1
        if row.ContactNameOut =='None':
            no_name += 1

    new_dict = {
        'Address Matches': address_match,
        'City Matches': city_match,
        'ZipCode Matches': zipcode_match,
        'No Address': no_address_count,
        'No Date': no_date_count,
        'Relevant Name': healthcount,
        'Business Phone': business_count,
        'Residential Phone': residential_count,
        'Low Quality': low_count,
        'Medium Quality': med_count,
        'High Quality': high_count,
        'Mailable': mailcount,
        'Connected': connectcount,
        'Ported': portcount,
        'Not Valid': novalidcount,
        'Unknown Contact': unknowncount,
        'Possibly Disconnected': disconnectedcount,
        'Possibly Portable VOIP': voipcount,
        'Wireless': wirelesscount,
        'First Name Match':first_name_match,
        'Last Name Match':last_name_match,
        'Workplace Match': workplace_match,
        'State Match': state_match, 
        'No Name': no_name
        }
        
    return(new_dict)

def clean_zipcode(zipcode):
    zipcode=str(zipcode)
    zipcode = zipcode.replace(".0","")
    if len(zipcode)==3:
        zipcode = "00"+zipcode
    if len(zipcode)==4: 
        zipcode = "0"+zipcode
    else:
        zipcode = zipcode[0:5]
    return(zipcode)