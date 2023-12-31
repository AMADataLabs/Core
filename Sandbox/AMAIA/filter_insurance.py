'''
This script merges insurance data with Masterfile data and selects those records that
are significant different
'''
import pgeocode

def sum_it_up(df):
    '''Remove matching addresses'''
    keep_list = []
    print("Removing matching addresses...")
    for row in df.itertuples():
        keep = False
        if row.POST_CD_ID_POLO != row.POST_CD_ID and row.POST_CD_ID != row.POST_CD_ID_PPMA:
            if row.STATE_CD != row.STATE_CD_PPMA and row.STATE_CD != row.STATE_CD_POLO:
                if row.CITY != row.CITY_PPMA and row.CITY != row.CITY_POLO:
                    if row.ZIP != row.ZIP_PPMA and row.ZIP != row.ZIP_POLO:
                        if row.ADDR_1 != row.ADDR_1_PPMA and row.ADDR_1 != row.ADDR_1_POLO:
                            keep = True
        keep_list.append(keep)
    df['NEW'] = keep_list
    df = df[df.NEW==True]
    return df

def get_zip_distance(zip1, zip2, dist):
    '''Get distances between zipcodes'''
    zip1 = clean_zipcode(zip1)
    zip2 = clean_zipcode(zip2)
    distance = dist.query_postal_code(zip1, zip2)*0.621371
    return distance

def clean_zipcode(zipcode):
    '''Format zipcode'''
    zipcode = str(zipcode)
    zipcode = zipcode.replace(" ", "")
    zipcode = zipcode.replace(".0", "")
    if len(zipcode) == 3:
        zipcode = "00"+zipcode
    if len(zipcode) == 4:
        zipcode = "0"+zipcode
    else:
        zipcode = zipcode[0:5]
    return zipcode

def get_zip_distances(df):
    '''Get all zip distances'''
    polo_dists = []
    ppma_dists = []
    print("Removing significantly close addresses...")
    dist = pgeocode.GeoDistance('US')
    for row in df.itertuples():
        polo_dists.append(get_zip_distance(row.ZIP_POLO, row.ZIP, dist))
        ppma_dists.append(get_zip_distance(row.ZIP_PPMA, row.ZIP, dist))
    df['POLO_DISTANCE'] = polo_dists
    df['PPMA_DISTANCE'] = ppma_dists
    return df

def get_far_places(df):
    '''Remove close addresses'''
    new_df = df[(df.POLO_DISTANCE > 200) & (df.PPMA_DISTANCE > 200)]
    return new_df

def filter_insurance(insurance):
    '''Filter'''
    ins = sum_it_up(insurance)
    ins = get_zip_distances(ins)
    ins = get_far_places(ins)
    return(ins)
