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

        if row.Address == row.OFFICE_ADDRESS_LINE_2:
            address_match = 1
        if row.City == row.OFFICE_ADDRESS_CITY:
            city_match = 1
        if row.Zipcode == row.OFFICE_ADDRESS_ZIP:
            zipcode_match = 1
        if row.State == row.OFFICE_ADDRESS_STATE:
            state_match = 1
        
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.Name).lower():
            last_name_match =1
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.Name).lower():
            first_name_match =1

        if is_healthy(row.Name) == True:  
            health = 1

        if 'IsMailable' in str(row.Notes):
            mail = 1
        if 'IsConnected' in str(row.Notes):
            connect = 1
        if 'IsPorted' in str(row.Notes):
            port = 1
        if 'NotValid' in str(row.Notes):
            novalid = 0
        if 'IsUnknownContact' in str(row.Notes):
            unknown = 0
        if 'IsPossibleDisconnected' in str(row.Notes):
            disconnected = 0
        if 'IsPossiblePortableVOIP' in str(row.Notes):
            voip = 0
        if 'IsWireless' in str(row.Notes):
            wireless = 0

        if row.Address == 'None':
            address = 0
        if row.Date == 'None':
            date = 0
        if row.PhoneType == 'BUSINESS':
            business = 1
        if row.PhoneType == 'RESIDENTIAL':
            residential = 1
        if row.QualityScore == 'LOW':
            low = 1
        if row.QualityScore == 'HIGH':
            high = 1
        if row.QualityScore == 'MED':
            med = 1

        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.Name).lower():
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
            'Not Valid': novalid,
            'Unknown Contact': unknown,
            'Possibly Disconnected': disconnected,
            'Possibly Portable VOIP': voip,
            'Wireless': wireless,
            'First Name Match':first_name_match,
            'Last Name Match':last_name_match,
            'Workplace Match': workplace_match
            }

        LIST_OF_DICTS.append(new_dict)

    return(LIST_OF_DICTS)

        
            
    