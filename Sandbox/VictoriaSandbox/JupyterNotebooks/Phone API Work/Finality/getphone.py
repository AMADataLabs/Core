def variable_breakdown(dataframe, med_words):
    
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
        no_address = 0
        no_date = 0
        business = 0
        residential = 0
        low = 0
        high = 0
        med = 0
        first_name_match = 0
        last_name_match = 0 
        workplace_match = 0

        if row.Address == row.OFFICE_ADDRESS_LINE_2_y:
            address_match = 1
        if row.City == row.OFFICE_ADDRESS_CITY_y:
            city_match = 1
        if row.Zipcode == row.OFFICE_ADDRESS_ZIP_y:
            zipcode_match = 1
        if str(row.PHYSICIAN_LAST_NAME_y).lower() in str(row.Name).lower():
            last_name_match +=1

        if str(row.PHYSICIAN_FIRST_NAME_y).lower() in str(row.Name).lower():
            first_name_match +=1

        healthy = False
        for word in med_words:
            if word in str(row.Name).lower():
                healthy = True
        if healthy == True:    
            health = 1

        if 'IsMailable' in str(row.Notes):
            mail = 1
        if 'IsConnected' in str(row.Notes):
            connect = 1
        if 'IsPorted' in str(row.Notes):
            port = 1
        if 'NotValid' in str(row.Notes):
            novalid = 1
        if 'IsUnknownContact' in str(row.Notes):
            unknown = 1
        if 'IsPossibleDisconnected' in str(row.Notes):
            disconnected = 1
        if 'IsPossiblePortableVOIP' in str(row.Notes):
            voip = 1
        if 'IsWireless' in str(row.Notes):
            wireless = 1

        if row.Address == 'None':
            no_address = 1
        if row.Date == 'None':
            no_date = 1
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

        if str(row.OFFICE_ADDRESS_LINE_1_y).lower() in str(row.Name).lower():
            workplace_match +=1

        new_dict = {
            'OFFICE_TELEPHONE': row.OFFICE_TELEPHONE,
            'Address Match': address_match,
            'City Match': city_match,
            'ZipCode Match': zipcode_match,
            'No Address': no_address,
            'No Date': no_date,
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

        
            
    