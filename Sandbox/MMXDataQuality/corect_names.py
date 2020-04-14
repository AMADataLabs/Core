import settings
import pandas as pd
from datalabs.access.edw import EDW
import logging
from collections import namedtuple

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

RuleForNames = namedtuple('RuleForNames', 'test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san')

def main():
    df = sql_query_get_data_edw()
    incorrect_dfs = rules_to_exclude_names(df)
    incorrect_df = append_excluded_names(incorrect_dfs)
    save_to_csv(incorrect_df)

def sql_query_get_data_edw():
    with EDW() as edw:
        data = edw.read("select distinct b.party_id, b.first_nm, b.middle_nm, b.last_nm, c.me_number \
                        from amaedw.party_cat a \
                        left outer join amaedw.person_nm b \
                        on a.party_id=b.party_id \
                        left outer join (select distinct party_id, key_val as me_number from amaedw.party_key where key_type_id=18 and active_ind='Y') c on a.party_id=c.party_id where a.cat_grp_id = 482 and a.cat_cd_id = 6664 and a.src_end_dt is null ")
    return data

def rules_to_exclude_names(data):
    test_user = data.loc[(data['FIRST_NM'].isin(['Test1', 'Z-Test'])) | (data['LAST_NM'].isin(['Testperson', 'Zzz03'])) \
                         | ((data['FIRST_NM'] == 'Consumer') & (data['MIDDLE_NM'] == 'Affairs') & (data['LAST_NM'] == 'Tester')) \
                         | (data['MIDDLE_NM'] == 'Nmn')]
    LOGGER.debug('Total names: %s for test_user', test_user.shape[0] )

    middle_to_last = data.loc[(data['FIRST_NM'] == data['LAST_NM']) & ~(data['MIDDLE_NM'].isna()) & (~data['FIRST_NM'].isin(['Test1', 'Z-Test']))]
    LOGGER.debug('Total names: %s for middle_to_last', middle_to_last.shape[0])

    last_nm_1 = data.loc[(data['FIRST_NM'] != data['LAST_NM']) & (data['LAST_NM'].str.len() == 1)]
    LOGGER.debug('Total names: %s for last_nm_1', last_nm_1.shape[0])

    last_nm_split = data.loc[data['LAST_NM'].isin(['Van', 'Von', 'Al', 'El', 'St']) & (data['FIRST_NM'] != data['LAST_NM'])]  # what if middle name is None
    LOGGER.debug('Total names: %s for last_nm_split', last_nm_split.shape[0])

    first_only = data.loc[(data['FIRST_NM'] == data['LAST_NM']) & data['MIDDLE_NM'].isna()]
    LOGGER.debug('Total names: %s for first_only', first_only.shape[0])

    remove_middle = data.loc[((data['FIRST_NM'] == data['MIDDLE_NM']) | (data['MIDDLE_NM'] == data['LAST_NM'])) & \
                             (data['MIDDLE_NM'] != 'Van') & (~data['FIRST_NM'].isin(['Test1', 'Z-Test']))]
    LOGGER.debug('Total names: %s for remove_middle', remove_middle.shape[0])

    de_la = data.loc[(data['LAST_NM'] == 'De') & (data['FIRST_NM'] == 'La')]
    LOGGER.debug('Total names: %s for de_la', de_la.shape[0])

    de = data.loc[(data['LAST_NM'] == 'La') & ~(data['MIDDLE_NM'].isna()) & (data['MIDDLE_NM'] != 'Tran')]
    LOGGER.debug('Total names: %s for la', de.shape[0])

    ben = data.loc[(data['LAST_NM'] == 'Ben') & (data['FIRST_NM'] == 'Abda')]
    LOGGER.debug('Total names: %s for ben', ben.shape[0])

    Del = data.loc[(data['LAST_NM'] == 'Del')]
    LOGGER.debug('Total names: %s for del', Del.shape[0])

    delle = data.loc[(data['LAST_NM'] == 'Delle')]
    LOGGER.debug('Total names: %s for delle', delle.shape[0])

    san = data.loc[(data['LAST_NM'] == 'San') & ((data['FIRST_NM'] == 'Jose') | (data['FIRST_NM'] == 'Juan'))]
    LOGGER.debug('Total names: %s for san', san.shape[0])
    #return test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san
    return RuleForNames(
        test_user=test_user,
        middle_to_last=middle_to_last,
        last_nm_1=last_nm_1,
        last_nm_split=last_nm_split,
        first_only=first_only,
        de_la=de_la,
        de=de,
        ben=ben,
        Del=Del,
        delle=delle,
        san=san
    )

def append_excluded_names(incorrect_dfs):
    incorrect_df = pd.DataFrame(columns=['PARTY_ID', 'FIRST_NM', 'MIDDLE_NM', 'LAST_NM', 'ME_NUMBER'])
    incorrect_df = incorrect_df.append([incorrect_dfs.test_user, incorrect_dfs.middle_to_last, incorrect_dfs.last_nm_1, incorrect_dfs.last_nm_split, incorrect_dfs.first_only, incorrect_dfs.de_la, incorrect_dfs.de, incorrect_dfs.ben, incorrect_dfs.Del, incorrect_dfs.delle, incorrect_dfs.san], ignore_index=True)
    return incorrect_df

def save_to_csv(incorrect_df):
    incorrect_df.to_csv('incorrect_names.csv')

main()

