from med_words4 import med_words
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
    
def is_healthy(name):
    healthy = False
    for word in med_words:
        if word in str(name).lower():
            healthy = True
    return(healthy)

addr_translate = {
    'DR': 'DRIVE',
    'PKWY': 'PARKWAY',
    'RD': 'ROAD',
    'ST': 'STREET',
    'STE': 'SUITE',
    'N': 'NORTH',
    'S': 'SOUTH',
    'E': 'EAST',
    'W': 'WEST',
    'LN': 'LANE',
    'CTR': 'CENTER',
    'CT': 'COURT',
    'BLVD': 'BOULEVARD',
    'CIR': 'CIRCLE',
    'HTS': 'HEIGHTS',
    'AVE': 'AVENUE',
    'HWY': 'HIGHWAY',
    'JCT': 'JUNCTION',
    'LK': 'LAKE',
    'MTN': 'MTN',
    'APT': 'APARTMENT',
    'RM': 'ROOM',
    'PL': 'PLACE',
    'PLZ': 'PLACA',
    'RDG': 'RIDGE',
    'SQ': 'SQUARE',
    'STA': 'STATION',
    'TER': 'TERRACE',
    'TRL': 'TRAIL',
    'TPKE': 'TURNPIKE',
    'VLY': 'VALLEY',
    'IS': 'ISLAND'
}


def translate_addr(addr_string):
    addr_string = addr_string.upper()
    new_addr = []
    
    tokens = addr_string.split()
    
    for t in tokens:
        if t in addr_translate:
            new_addr.append(addr_translate[t])
        else:
            new_addr.append(t)
    
    return ' '.join(new_addr)

def analyze_numbers(dataframe):
    
    address_match = 0
    city_match = 0
    zipcode_match = 0
    healthcount = 0
    mailcount = 0
    connectcount = 0
    portcount = 0
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
    SIC_count = 0
        


    for row in dataframe.itertuples():
        gpi_add = translate_addr(str(row.Address))
        ws_add = translate_addr(str(row.OFFICE_ADDRESS_LINE_2))
        if gpi_add != 'NONE':
            if gpi_add in ws_add or ws_add in gpi_add:
                address_match += 1
            elif fuzz.ratio(gpi_add, ws_add)>80:
                address_match+=1
        if str(row.OFFICE_ADDRESS_CITY) in str(row.City):
            city_match += 1
        if clean_zipcode(row.OFFICE_ADDRESS_ZIP) == clean_zipcode(row.Zipcode):
            zipcode_match += 1
        
        if row.State == row.OFFICE_ADDRESS_STATE:
            state_match += 1
        
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.Name).lower():
            last_name_match +=1
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.Name).lower():
            first_name_match +=1
        
        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.Name).lower():
            workplace_match += 1

        if is_healthy(row.Name)==True:    
            healthcount += 1

        if 'IsMailable' in str(row.Notes):
            mailcount += 1
        if 'IsConnected' in str(row.Notes):
            connectcount += 1
        if 'IsPorted' in str(row.Notes):
            portcount += 1
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
        if row.Name =='None':
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
        'Unknown Contact': unknowncount,
        'Possibly Disconnected': disconnectedcount,
        'Possibly Portable VOIP': voipcount,
        'Wireless': wirelesscount,
        'First Name Match':first_name_match,
        'Last Name Match':last_name_match,
        'Workplace Match': workplace_match,
        'State Match': state_match, 
        'No Name': no_name,
        'Relevant SIC': SIC_count
        }
        
    return(new_dict)

def variable_breakdown(dataframe):
    
    LIST_OF_DICTS = []
    
    
    for row in dataframe.itertuples():

        address_match = 0
        business = 0
        city_match = 0
        connect = 0
        no_date = 0
        disconnected = 0
        first_name_match = 0
        health = 0
        high = 0
        INF = 0
        last_name_match = 0 
        low = 0
        mail = 0
        med = 0
        no_address = 0
        no_provider = 0
        no_SIC = 0
        port = 0
        possible_portable_voip =0
        relevant_SIC =0
        residential = 0
        state_match = 0
        toll_free = 0
        unknown = 0
        voip = 0
        wireless_note =0
        workplace_match = 0
        zipcode_match = 0



        gpi_add = translate_addr(str(row.Address))
        ws_add = translate_addr(str(row.OFFICE_ADDRESS_LINE_2))
        if gpi_add != 'NONE':
            if gpi_add in ws_add or ws_add in gpi_add:
                address_match = 1
            elif fuzz.ratio(gpi_add, ws_add)>80:
                address_match+=1

        if row.PhoneType == 'BUSINESS':
            business = 1

        if str(row.OFFICE_ADDRESS_CITY) in str(row.City):
            city_match = 1

        if 'IsConnected' in str(row.Notes):
            connect = 1

        if row.Date == 'None':
            no_date = 1

        if 'IsPossibleDisconnected' in str(row.Notes):
            disconnected = 1
        
        if str(row.PHYSICIAN_FIRST_NAME).lower() in str(row.Name).lower():
            first_name_match = 1
            
        if is_healthy(row.Name) == True:  
            health = 1
        
        if row.QualityScore == 'HIGH':
            high = 1
        
        if 'INF' in str(row.Notes):
            INF = 1
        
        if str(row.PHYSICIAN_LAST_NAME).lower() in str(row.Name).lower():
            last_name_match =1

        if row.QualityScore == 'LOW':
            low = 1

        if 'IsMailable' in str(row.Notes):
            mail = 1

        if row.QualityScore == 'MED':
            med =1

        if row.Address == 'None':
            no_address = 1

        if row.Provider == 'None':
            no_provider = 1
    

        if row.SICDesc == 'None':
            no_SIC = 1

        if 'IsPorted' in str(row.Notes):
            port = 1
        
        if 'IsPossiblePortableVOIP' in str(row.Notes):
            possible_portable_voip = 1

        if is_healthy(row.SICDesc) == True:
            relevant_SIC = 1
            
        if row.PhoneType == 'RESIDENTIAL':
            residential = 1
            
        if row.State == row.OFFICE_ADDRESS_STATE:
            state_match = 1

        if 'IsTollFreeNumber' in str(row.Notes):
            toll_free = 1

        if 'IsUnknownContact' in str(row.Notes):
            unknown = 1

        if row.PhoneType == 'UNKNOWN':
            unknown_phone_type = 1

        
        if 'IsWireless' in str(row.Notes):
            wireless_note = 1


        if str(row.OFFICE_ADDRESS_LINE_1).lower() in str(row.Name).lower():
            workplace_match = 1

        if clean_zipcode(row.OFFICE_ADDRESS_ZIP) == clean_zipcode(row.Zipcode):
            zipcode_match = 1
        
        


        new_dict = {
            'OFFICE_TELEPHONE': row.Phone,
            'Address Match': address_match,
            'Business Phone': business,
            'City Match': city_match,
            'Connected': connect,
            'Disconnected':disconnected,
            'First Name Match':first_name_match,
            'High Quality': high,
            'INF': INF,
            'Last Name Match':last_name_match,
            'Low Quality': low,
            'Mailable': mail,
            'Medium Quality': med,
            'No Address': no_address,
            'No Provider': no_provider,
            'NO SIC': no_SIC,
            'No Date': no_date,
            'Ported': port,
            'Possibly Portable VOIP': possible_portable_voip,
            'Relevant Name': health,
            'Relevant SIC': relevant_SIC,
            'Residential Phone': residential,
            'State Match': state_match,
            'Toll free': toll_free,
            'Unknown Contact': unknown,
            'Unknown phone type':unknown_phone_type,
            'Workplace Match': workplace_match,
            'ZipCode Match': zipcode_match,
            'Wireless note': wireless_note,
            'VOIP': voip
            }

        LIST_OF_DICTS.append(new_dict)

    return(LIST_OF_DICTS)