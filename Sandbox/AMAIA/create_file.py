'''Create ingest file'''
from datetime import date
import pandas as pd
import settings
from datalabs.access.edw import EDW

def get_query():
    '''Get usage query'''
    sql_query = \
        '''
        SELECT DISTINCT
        A.PARTY_ID,
        A.POST_CD_ID,
        P.ADDR_1,
        P.ADDR_2,
        P.ADDR_3,
        P.CITY,
        S.SRC_STATE_CD AS STATE_CD,
        P.SRC_POST_KEY,
        P.POST_CD AS ZIP,
        A.FROM_DT,
        P.SRC_POST_KEY AS POST_KEY,
        C.PURPOSE_TYPE_DESC,
        C.PURPOSE_TYPE_ID,
        C.PURPOSE_USG_DESC
        FROM
        AMAEDW.POST_CD P, AMAEDW.STATE S , AMAEDW.PARTY_ADDR A, AMAEDW.CONT_PURPOSE_TYPE C
        WHERE
        A.PURPOSE_TYPE_ID=C.PURPOSE_TYPE_ID
        AND
        C.PURPOSE_CAT_CD='A'
        AND
        A.POST_CD_ID = P.POST_CD_ID
        AND
        P.STATE_ID = S.STATE_ID
        AND
        A.THRU_DT IS NULL
        ORDER BY A.FROM_DT DESC
        '''
    return sql_query

def get_bad_usages():
    '''Remove source restrictions'''
    bad_usages = ['License - California',
                  'License - Delaware',
                  'License - Montana',
                  'License - Nebraska',
                  'License - New Jersey',
                  'License - New York',
                  'License - Pennsylvania',
                  'License - Puerto Rico',
                  'License - Minnesota',
                  'License - Utah',
                  'License - Washington']
    return bad_usages

def get_other_usages():
    '''Get insurance data from EDW'''
    query = get_query()
    bad_usages = get_bad_usages()
    print('Getting usages...')
    with EDW() as edw:
        usage = edw.read(query)
        print('Filtering...')
    usage = usage[usage.PURPOSE_TYPE_DESC.isin(bad_usages) == False]
    usage = usage[usage.PURPOSE_USG_DESC != 'Preferred Professional Mailing Address']
    return usage

def get_col():
    '''Get column dict'''
    columns = {
        'ME':'me#',
        'SRC_POST_KEY':'comm_id',
        'ADDR_1_y':'addr_line_1',
        'ADDR_2_y':'addr_line_2',
        'ADDR_3_y':'addr_line_3',
        'CITY_y':'addr_city',
        'STATE_CD_y':'addr_state',
        'ZIP_y':'addr_zip'}
    return columns

def fix_me(me_list):
    '''Add leading zeroes to ME'''
    nums = []
    for num in me_list:
        num = str(num)
        num = num.replace('.0', '')
        if len(num) == 10:
            num = '0' + num
        elif len(num) == 9:
            num = '00' + num
        elif len(num) == 8:
            num = '000' + num
        nums.append(num)
    return nums

def clean_file(insurance, usage):
    '''Merge and clean data'''
    all_that = pd.merge(insurance, usage, on=['POST_CD_ID', 'PARTY_ID'])
    all_that = all_that[all_that.PURPOSE_USG_DESC != 'Insurance']
    nones = all_that.fillna('None')
    missing_addresses = all_that[(nones.ADDR_2_y == 'None')&
                                 (nones.ADDR_1_y == 'None')&
                                 (nones.ADDR_3_y != 'None')]
    missing_addresses['ADDR_1_y'] = missing_addresses.ADDR_3_y
    all_that = all_that[(nones.ADDR_2_y != 'None')&(nones.ADDR_1_y != 'None')]
    all_that = all_that[nones.STATE_CD_y != 'None']
    all_that = pd.concat([all_that, missing_addresses])
    all_that = all_that.drop_duplicates(['POST_CD_ID', 'PARTY_ID'])
    all_that['usage'] = 'PP'
    all_that['load_type_ind'] = 'R'
    all_that['source'] = 'INS-USG'
    all_that['addr_type'] = 'N'
    all_that['source_dtm'] = str(date.today())
    col = get_col()
    all_that = all_that[['ME',
                         'SRC_POST_KEY',
                         'usage',
                         'load_type_ind',
                         'addr_type',
                         'ADDR_1_y',
                         'ADDR_2_y',
                         'ADDR_3_y',
                         'CITY_y',
                         'STATE_CD_y',
                         'ZIP_y',
                         'source',
                         'source_dtm',
                         ]].rename(columns=col)
    all_that['me#'] = fix_me(all_that['me#'])
    return all_that

def extra_file(insurance, usage):
    '''maybe'''
    print('Merging...')
    all_that = pd.merge(insurance, usage, on=['POST_CD_ID', 'PARTY_ID'])
    all_that = all_that[all_that.PURPOSE_USG_DESC != 'Insurance']
    all_that = all_that.drop_duplicates(['POST_CD_ID', 'PARTY_ID'])
    col = get_col()
    all_that = all_that[['ME',
                         'SRC_POST_KEY',
                         'ADDR_1_y',
                         'ADDR_2_y',
                         'ADDR_3_y',
                         'CITY_y',
                         'STATE_CD_y',
                         'ZIP_y',
                         'PURPOSE_USG_DESC',
                         'PURPOSE_TYPE_DESC'
                         ]].rename(columns=col)
    all_that['me#'] = fix_me(all_that['me#'])
    return all_that

def create_file(insurance):
    '''Create final file'''
    usage = get_other_usages()
    final_file = clean_file(insurance, usage)
    return final_file

def get_extra_file():
    '''ugh'''
    usage = get_other_usages()
    insurance = pd.read_csv('C:/Users/vigrose/Data/AMAIA/Insurance_2020-11-17.csv')
    final_file = extra_file(insurance, usage)
    final_file.to_csv('C:/Users/vigrose/Data/AMAIA/Insurance_Source_2020-11-25.csv', index=False)

if __name__ == "__main__":
    get_extra_file()
