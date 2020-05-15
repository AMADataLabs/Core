'''
This script reads the latest insurance addresses from EDW
'''
from datetime import date
import pandas as pd
import settings
from datalabs.access.edw import EDW

def get_amaia_query():
    '''Define insurance query'''
    query = \
        """
        SELECT DISTINCT
        A.PARTY_ID,
        K.KEY_VAL AS ME,
        A.POST_CD_ID,
        A.FROM_DT,
        C.PURPOSE_TYPE_DESC AS ADDR_TYPE,
        P.ADDR_1,
        P.ADDR_2,
        P.ADDR_3,
        P.CITY,
        S.SRC_STATE_CD AS STATE_CD,
        P.POST_CD AS ZIP
        FROM
        AMAEDW.PARTY_KEY K, AMAEDW.PARTY_ADDR A, AMAEDW.CONT_PURPOSE_TYPE C, AMAEDW.POST_CD P,
        AMAEDW.STATE S
        WHERE
        A.THRU_DT IS NULL
        AND
        K.PARTY_ID = A.PARTY_ID
        AND
        K.KEY_TYPE_ID = 18
        AND
        K.ACTIVE_IND = 'Y'
        AND
        C.PURPOSE_TYPE_ID IN (1)
        AND
        A.POST_CD_ID = P.POST_CD_ID
        AND
        P.STATE_ID = S.STATE_ID
        ORDER BY A.FROM_DT DESC;
        """
    return query

def get_ppma_query():
    '''Get most recent mailing address query'''
    sql_query_ppma = \
    '''
    SELECT DISTINCT
    A.PARTY_ID,
    A.POST_CD_ID,
    P.ADDR_1,
    P.ADDR_2,
    P.ADDR_3,
    P.CITY,
    S.SRC_STATE_CD AS STATE_CD,
    P.POST_CD AS ZIP,
    A.FROM_DT
    FROM
    AMAEDW.POST_CD P, AMAEDW.STATE S , AMAEDW.PARTY_ADDR A, AMAEDW.CONT_PURPOSE_TYPE C
    WHERE
    A.PURPOSE_TYPE_ID=C.PURPOSE_TYPE_ID
    AND
    C.PURPOSE_CAT_CD='A'
    AND
    C.PURPOSE_USG_CD='PP'
    AND
    A.POST_CD_ID = P.POST_CD_ID
    AND
    P.STATE_ID = S.STATE_ID
    AND
    A.THRU_DT IS NULL
    ORDER BY A.FROM_DT DESC
        '''
    return sql_query_ppma

def get_polo_query():
    '''Get most recent office address query'''
    sql_query_polo = \
    '''
    SELECT DISTINCT
    A.PARTY_ID,
    A.POST_CD_ID,
    P.ADDR_1,
    P.ADDR_2,
    P.ADDR_3,
    P.CITY,
    S.SRC_STATE_CD AS STATE_CD,
    P.POST_CD AS ZIP,
    A.FROM_DT,
    P.SRC_POST_KEY AS POST_KEY
    FROM
    AMAEDW.POST_CD P, AMAEDW.STATE S , AMAEDW.PARTY_ADDR A, AMAEDW.CONT_PURPOSE_TYPE C
    WHERE
    A.PURPOSE_TYPE_ID=C.PURPOSE_TYPE_ID
    AND
    C.PURPOSE_CAT_CD='A'
    AND
    C.PURPOSE_USG_CD='PO'
    AND
    A.POST_CD_ID = P.POST_CD_ID
    AND
    P.STATE_ID = S.STATE_ID
    AND
    A.THRU_DT IS NULL
    ORDER BY A.FROM_DT DESC
    '''
    return sql_query_polo

def get_necessary_data():
    '''Get insurance data from EDW'''
    amaia_query = get_amaia_query()
    ppma_query = get_ppma_query()
    polo_query = get_polo_query()
    print('Connecting to edw...')
    with EDW() as edw:
        print('Getting insurance...')
        insurance = edw.read(amaia_query)
        print('Getting ppma...')
        ppma = edw.read(ppma_query)
        print('Getting polo...')
        polo = edw.read(polo_query)
    print('Dropping duplicates...')
    insurance = insurance.drop_duplicates(subset='PARTY_ID', keep='first')
    polo = polo.drop_duplicates(subset='PARTY_ID', keep='first')
    ppma = ppma.drop_duplicates(subset='PARTY_ID', keep='first')
    print('Merging...')
    ppma_polo = pd.merge(ppma, polo, on='PARTY_ID', how='outer', suffixes=('_PPMA', '_POLO'))
    insurance_ppma_polo = pd.merge(insurance, ppma_polo, on='PARTY_ID')

    return insurance_ppma_polo

def get_insurance():
    '''ahhhhhhhhhh'''
    insurance_ppma_polo = get_necessary_data()
    keep_list = []
    print('Iterating...')
    for row in insurance_ppma_polo.itertuples():
        keep = False
        if row.FROM_DT > row.FROM_DT_PPMA and row.FROM_DT > row.FROM_DT_POLO:
            keep = True
        keep_list.append(keep)
    insurance_ppma_polo['KEEP'] = keep_list
    return insurance_ppma_polo[insurance_ppma_polo.KEEP == True]

def save_insurance():
    '''Save'''
    TODAY = str(date.today())
    INSURANCE = get_insurance()
    print('Saving...')
    INSURANCE.to_csv(f'C:/Users/vigrose/Data/AMAIA/Insurance_{TODAY}.csv', index=False)

if __name__ == "__main__":
    save_insurance()
