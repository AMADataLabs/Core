'''Score'''

def score_addresses(full_table):
    '''Get address scores'''
    scored_addresses = []
    for row in full_table.itertuples():
        # add_1 = (row.DHC_Address_1_Match + row.Google_Address_1_Match + row.AMAIA_Address_1_Match + row.GetPhone_Address_1_Match)/row.Total_Records
        # add_2 = (row.DHC_Address_2_Match + row.Google_Address_2_Match + row.AMAIA_Address_2_Match + row.GetPhone_Address_2_Match)/row.Total_Records
        # add_3 = (row.DHC_Address_3_Match + row.Google_Address_3_Match + row.AMAIA_Address_3_Match + row.GetPhone_Address_3_Match)/row.Total_Records
        # city = (row.DHC_City_Match + row.Google_City_Match + row.AMAIA_City_Match + row.GetPhone_City_Match)/row.Total_Records
        # state = (row.DHC_State_Match + row.Google_State_Match + row.AMAIA_State_Match + row.GetPhone_State_Match)/row.Total_Records
        # zipcode = (row.DHC_Zip_Match + row.Google_Zip_Match + row.AMAIA_Zip_Match + row.GetPhone_Zip_Match)/row.Total_Records
        add_1 = (row.DHC_Address_1_Match + row.AMAIA_Address_1_Match)/row.Total_Records
        add_2 = (row.DHC_Address_2_Match + row.AMAIA_Address_2_Match)/row.Total_Records
        add_3 = (row.DHC_Address_3_Match + row.AMAIA_Address_3_Match)/row.Total_Records
        city = (row.DHC_City_Match + row.AMAIA_City_Match)/row.Total_Records
        state = (row.DHC_State_Match + row.AMAIA_State_Match)/row.Total_Records
        zipcode = (row.DHC_Zip_Match + row.AMAIA_Zip_Match)/row.Total_Records
        score_dict = {
            'ME': row.ME,
            'Address_2': row.Address_2,
            'Address_1_Match_Rate': add_1,
            'Address_2_Match_Rate': add_2,
            'Address_3_Match_Rate': add_3,
            'Zipcode_Match_Rate': zipcode,
            'City_Match_Rate': city,
            'State_Match_Rate': state,
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
