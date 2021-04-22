from   abc import ABC, abstractmethod
from   io import BytesIO

import csv
import logging
import pandas
import numpy as np
import pdb
import random
import string
from bisect import bisect_left, insort_left

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ContactIDMergeTransformerTask(etl.TransformerTask, ABC):
    def _transform(self):
        sfmc_contacts, active_subscription, users, api_orders = self._to_dataframe()

        sfmc_contacts = self._assign_id_to_contacts(sfmc_contacts)

        users, sfmc_contacts = self._assign_id_to_users(users, sfmc_contacts)

        api_orders = self._tranform_orders(api_orders)

        csv_data = [self._dataframe_to_csv(data) for data in [sfmc_contacts, active_subscription, users, api_orders]]

        return [data.encode('utf-8', errors='backslashreplace') for data in csv_data]

    def _to_dataframe(self):
        seperators = [',', ',', ',', ',']
        encodings_list = ['utf-8','utf-8','utf-8','utf-8' ]
        return [pandas.read_csv(BytesIO(data), sep=seperator, encoding = encodings, dtype = 'str', low_memory=False) for data, seperator, encodings in zip(self._parameters['data'], seperators, encodings_list)]

    def _assign_id_to_contacts(self, sfmc_contacts):
        id_list = []
        for ind in sfmc_contacts.index:
            if sfmc_contacts['HSContact_ID'][ind] != sfmc_contacts['HSContact_ID'][ind]:
                id = self.id_check(id_list, sfmc_contacts['HSContact_ID'])
                sfmc_contacts['HSContact_ID'][ind] = id
        return sfmc_contacts

    def id_check(self, id_list, existing_ids):
        x = self.id_generator()
        while True:
            id = self.BinarySearch(id_list, x, existing_ids)
            if id != 'nan':
                return id

    def id_generator(self, size=15, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def BinarySearch(self, id_list, x, existing_ids):
        i = bisect_left(id_list, x)
        if i != len(id_list) and id_list[i] == x:
            return 'nan'
        elif x in existing_ids:
            return 'nan'
        else:
            insort_left(id_list, x, lo=0, hi=len(id_list))
            return x

    def _assign_id_to_users(self, users, contacts):
        a = []
        id_list = []
        empty = []
        #users.insert(0, 'HSContact_ID', np.nan)
        for index_users in users.index:
            LOGGER.info(index_users)

            a = self.check_if_users_email_present_in_flatfile(index_users, contacts, users)

            if a.size >= 1:
                if str(contacts['NAME'][a[0]]).lower() == 'nan':

                    self.assign_users_contact_same_id_as_flatfile(index_users, a, contacts, users)

                    self.copy_contact_name_from_users_to_flatfile(index_users, a, contacts, users)

                    self.assign_flatfile_the_source_datalabs(a, contacts)

                elif (str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])).lower() == str(
                        contacts['NAME'][a[0]]).lower():

                    self.assign_users_contact_same_id_as_flatfile(index_users, a, contacts, users)

                elif str(users['FIRST_NM'][index_users]).lower() == 'nan' and str(
                        users['LAST_NM'][index_users]).lower() == 'nan':

                    self.assign_users_contact_same_id_as_flatfile(index_users, a, contacts, users)

                else:
                    self.assign_users_contact_same_id_as_flatfile(index_users, a, contacts, users)

            elif a.size == 0:
                self.assign_new_id_to_users(index_users, users, id_list, empty)
                self.add_contact_from_users_to_flatfile(index_users, contacts, users)

        return users, contacts

    def check_if_users_email_present_in_flatfile(self, index_users, contacts, users):
        count = np.where(contacts['BEST_EMAIL'].astype(str).str.contains(users['EMAIL'][index_users]))[0]
        return count

    def copy_contact_name_from_users_to_flatfile(self, index_users, a, contacts, users):
        contacts['NAME'][a[0]] = str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])

    def assign_flatfile_the_source_datalabs(self, a, contacts):
        contacts['SOURCE_ORD'][a[0]] = 'DL'

    def assign_users_contact_same_id_as_flatfile(self, index_users, a, contacts, users):
        users['HSContact_ID'][index_users] = contacts['HSContact_ID'][a[0]]

    def assign_new_id_to_users(self, index_users, users, id_list, empty):
        if users['HSContact_ID'][index_users] != users['HSContact_ID'][index_users] :
            id = self.id_check(id_list, empty)
            users['HSContact_ID'][index_users] = id

    def add_contact_from_users_to_flatfile(self, index_users, contacts, users):
        name = str(users['FIRST_NM'][index_users]) + " " + str(users['LAST_NM'][index_users])
        contacts = contacts.append({'HSContact_ID': users['HSContact_ID'][index_users], 'NAME': name,
                                    'BEST_EMAIL': users['EMAIL'][index_users],
                                    'ADDR1': users['ADDRESS_LINE_1'][index_users],
                                    'ADDR2': users['ADDRESS_LINE_2'][index_users], 'CITY': users['CITY'][index_users],
                                    'STATE': users['STATE'][index_users], 'ZIP': users['ZIPCODE'][index_users],
                                    'BUSNAME': users['ORG_NAME'][index_users], 'BUSTITLE': users['TITLE'][index_users],
                                    'SOURCE_ORD': 'DL',
                                    'RECSEQ': str(int(contacts['RECSEQ'][contacts.tail(1).index.item()])+1)},
                                    ignore_index=True)

    def _transform_orders(self, api_orders):
        api_orders = self.drop_columns_not_required(api_orders)

        df = self.groupby_to_get_calculation_by_date(api_orders)

        cmon, fapa, rapp, licboard, fapp = self.get_dfs_filtered_by_item_number(df)

        cmon = self.groupby_cmon_df(cmon)
        fapa = self.groupby_fapa_df(fapa)
        fapp = self.groupby_fapp_df(fapp)
        licboard = self.groupby_licboard_df(licboard)
        rapp = self.groupby_rapp_df(rapp)

        merged_df = self.merge_all_dfs(cmon, fapa, rapp, licboard, fapp)
        result = self.calculate(merged_df)
        return result

    def drop_columns_not_required(self, api_orders):
        api_orders = api_orders.drop(columns=['Unnamed: 0'])
        api_orders = api_orders.drop(columns=['Isell Login'])
        return api_orders

    def groupby_to_get_calculation_by_date(self, api_orders):
        df = api_orders.groupby(['Month', 'Year', 'Item Number', 'Customer Number', 'Company Name',
                                 'Customer Category']).sum().reset_index()
        return df

    def get_dfs_filtered_by_item_number(self, df):
        CMON = df.loc[df['Item Number'] == 'CMON']
        FAPA = df.loc[df['Item Number'] == 'FAPA']
        RAPP = df.loc[df['Item Number'] == 'RAPP']
        LICBOARD = df.loc[df['Item Number'] == 'LICBOARD']
        FAPP = df.loc[df['Item Number'] == 'FAPP']

        return CMON, FAPA, RAPP, LICBOARD, FAPP

    def groupby_cmon_df(self, CMON):
        CMON = CMON.groupby(['Month', 'Year', 'Item Number', 'Customer Number', 'Company Name',
                             'Customer Category']).sum().reset_index()
        CMON = CMON.rename(columns={"Num_Profs": "CM Profiles", "Rev": "CM Rev"})
        CMON = CMON.drop(columns=['Item Number'])

        return CMON

    def groupby_fapa_df(self, FAPA):
        FAPA = FAPA.groupby(['Month', 'Year', 'Item Number', 'Customer Number', 'Company Name',
                             'Customer Category']).sum().reset_index()
        FAPA = FAPA.rename(columns={"Num_Profs": "PA Profiles", "Rev": "PA Rev"})
        FAPA = FAPA.drop(columns=['Item Number'])

        return FAPA

    def groupby_rapp_df(self, RAPP):
        RAPP = RAPP.groupby(['Month', 'Year', 'Item Number', 'Customer Number', 'Company Name',
                             'Customer Category']).sum().reset_index()
        RAPP = RAPP.rename(columns={"Num_Profs": "Reapp Profiles", "Rev": "Reapp Rev"})
        RAPP = RAPP.drop(columns=['Item Number'])

        return RAPP

    def groupby_licboard_df(self, LICBOARD):
        LICBOARD = LICBOARD.groupby(['Month', 'Year', 'Item Number', 'Customer Number', 'Company Name',
                                     'Customer Category']).sum().reset_index()
        LICBOARD = LICBOARD.rename(columns={"Num_Profs": "LicBoard Profiles", "Rev": "LicBoard Rev"})
        LICBOARD = LICBOARD.drop(columns=['Item Number'])

        return LICBOARD

    def groupby_fapp_df(self, FAPP):
        FAPP = FAPP.groupby(['Month', 'Year', 'Item Number', 'Customer Number', 'Company Name',
                             'Customer Category']).sum().reset_index()
        FAPP = FAPP.rename(columns={"Num_Profs": "Full Profiles", "Rev": "Full Rev"})
        FAPP = FAPP.drop(columns=['Item Number'])

        return FAPP

    def merge_all_dfs(self, CMON, FAPA, RAPP, LICBOARD, FAPP ):
        cmon_fapa = pd.merge(CMON, FAPA, how='left',
                             left_on=['Month', 'Year', 'Customer Number', 'Company Name', 'Customer Category'],
                             right_on=['Month', 'Year', 'Customer Number', 'Company Name', 'Customer Category'])
        cmon_fapa_rapp = pd.merge(cmon_fapa, RAPP, how='left',
                                  left_on=['Month', 'Year', 'Customer Number', 'Company Name', 'Customer Category'],
                                  right_on=['Month', 'Year', 'Customer Number', 'Company Name', 'Customer Category'])
        cmon_fapa_rapp_fapp = pd.merge(cmon_fapa_rapp, FAPP, how='left',
                                       left_on=['Month', 'Year', 'Customer Number', 'Company Name',
                                                'Customer Category'],
                                       right_on=['Month', 'Year', 'Customer Number', 'Company Name',
                                                 'Customer Category'])
        cmon_fapa_rapp_fapa_licboard = pd.merge(cmon_fapa_rapp_fapp, LICBOARD, how='left',
                                                left_on=['Month', 'Year', 'Customer Number', 'Company Name',
                                                         'Customer Category'],
                                                right_on=['Month', 'Year', 'Customer Number', 'Company Name',
                                                          'Customer Category'])

        cmon_fapa_rapp_fapa_licboard = cmon_fapa_rapp_fapa_licboard.fillna(0)

        return cmon_fapa_rapp_fapa_licboard

    def calculate(self, cmon_fapa_rapp_fapa_licboard):
        cmon_fapa_rapp_fapa_licboard['Total Profiles'] = cmon_fapa_rapp_fapa_licboard['PA Profiles'] + \
                                                         cmon_fapa_rapp_fapa_licboard['Reapp Profiles'] + \
                                                         cmon_fapa_rapp_fapa_licboard['Full Profiles'] + \
                                                         cmon_fapa_rapp_fapa_licboard['LicBoard Profiles']
        cmon_fapa_rapp_fapa_licboard['Total Revenue'] = cmon_fapa_rapp_fapa_licboard['PA Rev'] + \
                                                        cmon_fapa_rapp_fapa_licboard['Reapp Rev'] + \
                                                        cmon_fapa_rapp_fapa_licboard['Full Rev'] + \
                                                        cmon_fapa_rapp_fapa_licboard['LicBoard Rev'] + \
                                                        cmon_fapa_rapp_fapa_licboard['CM Rev']
        cmon_fapa_rapp_fapa_licboard.insert(0, 'Order Begin Date', np.nan)
        cmon_fapa_rapp_fapa_licboard.insert(3, 'Isell Login', np.nan)
        cmon_fapa_rapp_fapa_licboard['Order Begin Date'] = "1" + "/" + cmon_fapa_rapp_fapa_licboard['Month'].astype(
            str) + "/" + cmon_fapa_rapp_fapa_licboard['Year'].astype(str)

        return cmon_fapa_rapp_fapa_licboard

    @classmethod
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)

