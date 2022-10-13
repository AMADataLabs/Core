def find_address_matches(new_addresses):
    '''Gahhh'''
    new_addresses = new_addresses.fillna('None')
    iqvia_states = []
    symph_states = []
    iqvia_citys = []
    symph_citys = []
    iqvia_zips = []
    symph_zips = []
    iqvia_adds = []
    symph_adds = []
    iqvia_adds_3 = []
    symph_adds_3 = []
    iqvia_names = []
    symph_names = []
    symph_phones = []
    totals = []

    for row in new_addresses.itertuples():
        state_symph = 0
        city_symph = 0
        zip_symph = 0
        add_symph = 0
        add_3_symph = 0
        name_symph = 0
        state_ins = 0
        city_ins = 0
        zip_ins = 0
        add_ins = 0
        add_3_ins = 0
        name_ins = 0

        if int(row.Phone) == int(row.Phone_Complete):
            symph_phone = 1
        if row.State_New == row.State_symph:
            state_symph = 1
            if row.City_symph == row.City_New:
                city_symph = 1
                if row.Zipcode == row.Zip_Code:
                    zip_symph = 1
                if check_match(row.Address, row.Address_2):
                    add_symph = 1
                if check_match(row.Address, row.Address_3):
                    add_3_symph = 1
                if check_match(row.Primary_Hospital_Affiliation, row.Address_1):
                    name_symph = 1
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

        iqvia_states.append(state_ins)
        symph_states.append(state_symph)
        iqvia_citys.append(city_ins)
        symph_citys.append(city_symph)
        iqvia_zips.append(zip_ins)
        symph_zips.append(zip_symph)
        iqvia_adds.append(add_ins)
        symph_adds.append(add_symph)
        iqvia_adds_3.append(add_3_ins)
        symph_adds_3.append(add_3_symph)
        iqvia_names.append(name_ins)
        symph_names.append(name_symph)
        symph_phones.append(symph_phone)
        totals.append(count_found(row))

    new_addresses['iqvia_State_Match'] = iqvia_states
    new_addresses['iqvia_City_Match'] = iqvia_citys
    new_addresses['iqvia_Zip_Match'] = iqvia_zips
    new_addresses['iqvia_Address_1_Match'] = iqvia_names
    new_addresses['iqvia_Address_2_Match'] = iqvia_adds
    new_addresses['iqvia_Address_3_Match'] = iqvia_adds_3
    new_addresses['symph_State_Match'] = symph_states
    new_addresses['symph_City_Match'] = symph_citys
    new_addresses['symph_Zip_Match'] = symph_zips
    new_addresses['symph_Address_1_Match'] = symph_names
    new_addresses['symph_Address_2_Match'] = symph_adds
    new_addresses['symph_Address_3_Match'] = symph_adds_3
    new_addresses['symph_Phone_Match'] = symph_phones
    new_addresses['Total_Records'] = totals

    return new_addresses

    def score_addresses(full_table):
    '''Get address scores'''
    scored_addresses = []
    for row in full_table.itertuples():
        address_key = f'{row.Address_2}_{row.Zipcode}
        symph = (row.symph_Address_2_Match + row.symph_Zip_Match)/2
        iqvia = (row.iqvia_Address_2_Match + row.iqvia_Zip_Match)/2
        dhc = (row.DHC_Address_2_Match + row.DHC_Zip_Match)/2
        amaia = (row.AMAIA_Address_2_Match + row.AMAIA_Zip_Match)/2
        match_rate = (symph + dhc + amaia + iqvia)/row.Total_Records
        score_dict = {
            'ME': row.ME,
            'ADDRESS_KEY': address_key,
            'MATCH_RATE': match_rate,
            'DATE': today
        }
        scored_addresses.append(score_dict)
    return scored_addresses