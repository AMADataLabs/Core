'''Score'''

def score_addresses(full_table):
    '''Get address scores'''
    scored_addresses = []
    for row in full_table.itertuples():
        add_1 = row.DHC_Address_1_Match + row.Google_Address_1_Match + row.AMAIA_Address_1_Match + row.GetPhone_Address_1_Match
        add_2 = row.DHC_Address_2_Match + row.Google_Address_2_Match + row.AMAIA_Address_2_Match + row.GetPhone_Address_2_Match
        add_3 = row.DHC_Address_3_Match + row.Google_Address_3_Match + row.AMAIA_Address_3_Match + row.GetPhone_Address_3_Match
        city = row.DHC_City_Match + row.Google_City_Match + row.AMAIA_City_Match + row.GetPhone_City_Match
        state = row.DHC_State_Match + row.Google_State_Match + row.AMAIA_State_Match + row.GetPhone_State_Match
        zipcode = row.DHC_Zip_Match + row.Google_Zip_Match + row.AMAIA_Zip_Match + row.GetPhone_Zip_Match
        score_dict = {
            'ME': row.ME,
            'Address_2': row.Address_2,
            'Address_1_Match_Rate': add_1/4,
            'Address_2_Match_Rate': add_2/4,
            'Address_3_Match_Rate': add_3/4,
            'Zipcode_Match_Rate': zipcode/4,
            'City_Match_Rate': city/4,
            'State_Match_Rate': state/4,
        }
        scored_addresses.append(score_dict)
    return scored_addresses

def score_phone_address_links(full_table):
    '''Get phone-address scores'''
    scored_phones = []
    for row in full_table.itertuples():
        link = row.Google_Name_Match + row.GetPhone_Name_Match + row.DHC_Phone_Match
        phone_dict = {
            'ME': row.ME,
            'Address_2': row.Address_2,
            'Master_Phone': row.Phone_Complete,
            'Phone_Address_Match': link/3
        }
        scored_phones.append(phone_dict)
    return scored_phones
