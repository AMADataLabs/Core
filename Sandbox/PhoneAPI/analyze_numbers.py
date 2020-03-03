def analyze_numbers(dataframe, med_words):
    
    
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

        


    for row in dataframe.itertuples():
        if row.Address == row.OFFICE_ADDRESS_LINE_2:
            address_match += 1
        if row.City == row.OFFICE_ADDRESS_CITY:
            city_match += 1
        if row.Zipcode == row.OFFICE_ADDRESS_ZIP:
            zipcode_match += 1
        
        if row.State == row.OFFICE_ADDRESS_STATE:
            state_match = 1
        
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.Name).lower():
            last_name_match +=1
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.Name).lower():
            first_name_match +=1
        
        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.Name).lower():
            workplace_match += 1

        healthy = False
        for word in med_words:
            if word in str(row.Name).lower():
                healthy = True
        if healthy == True:    
            healthcount += 1

        if 'IsMailable' in str(row.Notes):
            mailcount += 1
        if 'IsConnected' in str(row.Notes):
            connectcount += 1
        if 'IsPorted' in str(row.Notes):
            portcount += 1
        if 'NotValid' in str(row.Notes):
            novalidcount += 1
        if 'IsUnknownContact' in str(row.Notes):
            unknowncount += 1
        if 'IsPossibleDisconnected' in str(row.Notes):
            disconnectedcount += 1
        if 'IsPossiblePortableVOIP' in str(row.Notes):
            voipcount += 1
        if 'IsWireless' in str(row.Notes):
            wirelesscount += 1

        if row.Address == 'None':
            no_address_count += 1
        if row.Date == 'None':
            no_date_count += 1
        if row.PhoneType == 'BUSINESS':
            business_count += 1
        if row.PhoneType == 'RESIDENTIAL':
            residential_count += 1
        if row.QualityScore == 'LOW':
            low_count += 1
        if row.QualityScore == 'HIGH':
            high_count += 1
        if row.QualityScore == 'MED':
            med_count += 1

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
        }
        
    return(new_dict)
