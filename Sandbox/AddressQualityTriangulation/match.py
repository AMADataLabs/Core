'''Match'''
from fuzzywuzzy import fuzz

def check_match(thing_1, thing_2):
    '''match check'''
    if thing_1 == thing_2:
        return 1
    elif thing_1 in thing_2 or thing_2 in thing_1:
        return 1
    elif fuzz.ratio(thing_1, thing_2) > 70:
        return 1
    else:
        return 0

def find_address_matches(new_addresses):
    '''Gahhh'''
    new_addresses = new_addresses.fillna('None')
    amaia_states = []
    dhc_states = []
    amaia_citys = []
    dhc_citys = []
    amaia_zips = []
    dhc_zips = []
    amaia_adds = []
    dhc_adds = []
    amaia_adds_3 = []
    dhc_adds_3 = []
    amaia_names = []
    dhc_names = []
    dhc_phones = []

    for row in new_addresses.itertuples():
        state_dhc = 0
        city_dhc = 0
        zip_dhc = 0
        add_dhc = 0
        add_3_dhc = 0
        name_dhc = 0
        state_ins = 0
        city_ins = 0
        zip_ins = 0
        add_ins = 0
        add_3_ins = 0
        name_ins = 0
        office_ins = 0
        office_ins = 0
        if int(row.Phone) == int(row.Phone_Complete):
            dhc_phone = 1
        if row.State_New == row.State_DHC:
            state_dhc = 1
            if row.City_DHC == row.City_New:
                city_dhc = 1
                if row.Zipcode == row.Zip_Code:
                    zip_dhc = 1
                if check_match(row.Address, row.Address_2):
                    add_dhc = 1
                if check_match(row.Address, row.Address_3):
                    add_3_dhc = 1
                if check_match(row.Primary_Hospital_Affiliation, row.Address_1):
                    name_dhc = 1
        if row.STATE_CD == row.State_New:
            state_ins = 1
            if check_match(row.CITY, row.City_New):
                city_ins = 1
                if row.ZIP == row.Zipcode:
                    zip_ins = 1
                if check_match(row.ADDR_1, row.Address_2):
                    add_ins = 1
                if check_match(row.ADDR_2, row.Address_2):
                    add_ins = 1
                if check_match(row.ADDR_2, row.Address_1):
                    name_ins = 1
                if check_match(row.ADDR_3, row.Address_1):
                    name_ins = 1
                if check_match(row.ADDR_3, row.Address_3):
                    add_3_ins = 1
                if check_match(row.ADDR_1, row.Address_3):
                    add_3_ins = 1

        amaia_states.append(state_ins)
        dhc_states.append(state_dhc)
        amaia_citys.append(city_ins)
        dhc_citys.append(city_dhc)
        amaia_zips.append(zip_ins)
        dhc_zips.append(zip_dhc)
        amaia_adds.append(add_ins)
        dhc_adds.append(add_dhc)
        amaia_adds_3.append(add_ins)
        dhc_adds_3.append(add_dhc)
        amaia_names.append(name_ins)
        dhc_names.append(name_dhc)
        dhc_phones.append(dhc_phone)

    new_addresses['AMAIA_State_Match'] = amaia_states
    new_addresses['AMAIA_City_Match'] = amaia_citys
    new_addresses['AMAIA_Zip_Match'] = amaia_zips
    new_addresses['AMAIA_Address_1_Match'] = amaia_names
    new_addresses['AMAIA_Address_2_Match'] = amaia_adds
    new_addresses['AMAIA_Address_3_Match'] = amaia_adds_3
    new_addresses['DHC_State_Match'] = dhc_states
    new_addresses['DHC_City_Match'] = dhc_citys
    new_addresses['DHC_Zip_Match'] = dhc_zips
    new_addresses['DHC_Address_1_Match'] = dhc_names
    new_addresses['DHC_Address_2_Match'] = dhc_adds
    new_addresses['DHC_Address_3_Match'] = dhc_adds_3
    new_addresses['DHC_Phone_Match'] = dhc_phones

    return new_addresses

def find_phone_address_matches(new_addresses):
    '''Gahhh'''
    getphone_states = []
    google_states = []
    getphone_citys = []
    google_citys = []
    getphone_zips = []
    google_zips = []
    getphone_adds = []
    google_adds = []
    getphone_adds_3 = []
    google_adds_3 = []
    getphone_office = []
    google_office = []
    getphone_names = []
    google_names = []

    for row in new_addresses.itertuples():
        state_gf = 0
        city_gf = 0
        zip_gf = 0
        add_gf = 0
        add_3_gf = 0
        name_gf = 0
        state_google = 0
        city_google = 0
        zip_google = 0
        add_google = 0
        add_3_google = 0
        name_google = 0
        office_google = 0
        office_gf = 0

        if row.State_New == row.State_Google:
            state_google = 1
            if row.City_Google == row.City_New:
                city_google = 1
                if row.Zipcode == row.Zipcode_Reverse:
                    zip_google = 1
                if check_match(row.Address_Google, row.Address_2):
                    add_google = 1
                if check_match(row.Complete_Address, row.Address_2):
                    add_google = 1
                if check_match(row.Address_1, row.Name_Google):
                    office_google = 1
                if check_match(row.Address_3, row.Complete_Address):
                    add_3_google = 1
        if check_match(row.Physician_Name, row.Name_Google):
            name_google = 1

        if row.State_GetPhone == row.State_New:
            state_gf = 1
            if check_match(row.City_GetPhone, row.City_New):
                city_gf = 1
                if row.Zipcode_GetPhone == row.Zipcode:
                    zip_gf = 1
                if check_match(row.Address_GetPhone, row.Address_2):
                    add_gf = 1
                if check_match(row.Address_GetPhone, row.Address_3):
                    add_3_gf = 1
                if check_match(row.Address_1, row.Name_GetPhone):
                    office_gf = 1
        if check_match(row.Physician_Name, row.Name_GetPhone):
            name_gf = 1

        google_states.append(state_google)
        getphone_states.append(state_gf)
        google_citys.append(city_google)
        getphone_citys.append(city_gf)
        google_zips.append(zip_google)
        getphone_zips.append(zip_gf)
        google_adds.append(add_google)
        getphone_adds.append(add_gf)
        google_adds_3.append(add_3_google)
        getphone_adds_3.append(add_3_gf)
        google_names.append(name_google)
        getphone_names.append(name_gf)
        google_office.append(office_google)
        getphone_office.append(office_gf)

    new_addresses['GetPhone_State_Match'] = getphone_states
    new_addresses['GetPhone_City_Match'] = getphone_citys
    new_addresses['GetPhone_Zip_Match'] = getphone_zips
    new_addresses['GetPhone_Address_1_Match'] = getphone_office
    new_addresses['GetPhone_Address_2_Match'] = getphone_adds
    new_addresses['GetPhone_Address_3_Match'] = getphone_adds_3
    new_addresses['GetPhone_Name_Match'] = getphone_names
    new_addresses['Google_State_Match'] = google_states
    new_addresses['Google_City_Match'] = google_citys
    new_addresses['Google_Zip_Match'] = google_zips
    new_addresses['Google_Address_1_Match'] = google_office
    new_addresses['Google_Address_2_Match'] = google_adds
    new_addresses['Google_Address_3_Match'] = google_adds_3
    new_addresses['Google_Name_Match'] = google_names

    return new_addresses