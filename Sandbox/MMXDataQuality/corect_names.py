import settings
import pandas as pd
from datalabs.access.edw import EDW

def sql_query_get_data_edw():
    with EDW() as edw:
        data = edw.read("select distinct b.party_id, b.first_nm, b.middle_nm, b.last_nm, c.me_number \
                        from amaedw.party_cat a \
                        left outer join amaedw.person_nm b \
                        on a.party_id=b.party_id \
                        left outer join (select distinct party_id, key_val as me_number from amaedw.party_key where key_type_id=18 and active_ind='Y') c on a.party_id=c.party_id where a.cat_grp_id = 482 and a.cat_cd_id = 6664 and a.src_end_dt is null ")
    return data
def rules_to_exclude_names(data):
    test_user = data.loc[
        (data['FIRST_NM'].isin(['Test1', 'Z-Test'])) | (data['LAST_NM'].isin(['Testperson', 'Zzz03'])) | (
                    (data['FIRST_NM'] == 'Consumer') & (data['MIDDLE_NM'] == 'Affairs') & (
                        data['LAST_NM'] == 'Tester')) | (data['MIDDLE_NM'] == 'Nmn')]
    print(test_user.shape[0], 'test_user')

    middle_to_last = data.loc[(data['FIRST_NM'] == data['LAST_NM']) & ~(data['MIDDLE_NM'].isna()) & (
        ~data['FIRST_NM'].isin(['Test1', 'Z-Test']))]
    print(middle_to_last.shape[0], 'middle_to_last')

    last_nm_1 = data.loc[(data['FIRST_NM'] != data['LAST_NM']) & (data['LAST_NM'].str.len() == 1)]
    print(last_nm_1.shape[0], 'last_nm_1')

    last_nm_split = data.loc[data['LAST_NM'].isin(['Van', 'Von', 'Al', 'El', 'St']) & (data['FIRST_NM'] != data['LAST_NM'])]  # what if middle name is None
    print(last_nm_split.shape[0], 'last_nm_split')

    first_only = data.loc[(data['FIRST_NM'] == data['LAST_NM']) & data['MIDDLE_NM'].isna()]
    print(first_only.shape[0], 'first_only')

    remove_middle = data.loc[((data['FIRST_NM'] == data['MIDDLE_NM']) | (data['MIDDLE_NM'] == data['LAST_NM'])) & (data['MIDDLE_NM'] != 'Van') & (~data['FIRST_NM'].isin(['Test1', 'Z-Test']))]
    print(remove_middle.shape[0], 'remove_middle')

    de_la = data.loc[(data['LAST_NM'] == 'De') & (data['FIRST_NM'] == 'La')]
    print(de_la.shape[0], 'de_la')

    de = data.loc[(data['LAST_NM'] == 'La') & ~(data['MIDDLE_NM'].isna()) & (data['MIDDLE_NM'] != 'Tran')]
    print(de.shape[0], 'la')

    ben = data.loc[(data['LAST_NM'] == 'Ben') & (data['FIRST_NM'] == 'Abda')]
    print(ben.shape[0], 'ben')

    Del = data.loc[(data['LAST_NM'] == 'Del')]
    print(Del.shape[0], 'del')

    delle = data.loc[(data['LAST_NM'] == 'Delle')]
    print(delle.shape[0], 'delle')

    san = data.loc[(data['LAST_NM'] == 'San') & ((data['FIRST_NM'] == 'Jose') | (data['FIRST_NM'] == 'Juan'))]
    print(san.shape[0], 'san')
    return test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san

def append_excluded_names(test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san):
    incorrect_df = pd.DataFrame(columns=['PARTY_ID', 'FIRST_NM', 'MIDDLE_NM', 'LAST_NM', 'ME_NUMBER'])
    incorrect_df = incorrect_df.append([test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san], ignore_index=True)
    return incorrect_df

def save_to_csv(incorrect_df):
    incorrect_df.to_csv('incorrect_names.csv')

def main():
    df = sql_query_get_data_edw()
    test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san = rules_to_exclude_names(df)
    incorrect_df =append_excluded_names(test_user, middle_to_last, last_nm_1, last_nm_split, first_only, de_la, de, ben, Del, delle, san)
    save_to_csv(incorrect_df )

main()