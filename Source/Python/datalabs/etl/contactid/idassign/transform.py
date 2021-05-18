from   abc import ABC, abstractmethod
from   io import BytesIO

import csv
import logging
import pandas
import numpy as np
import pdb
import string

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ContactIDAssignTransformerTask(etl.TransformerTask, ABC):
    def _transform(self):
        sfmc_contacts, sfmc_contacts_old, users, users_old = self._to_dataframe()

        sfmc_contacts = self._assign_id_to_new_sfmc_data(sfmc_contacts, sfmc_contacts_old)

        users = self._assign_id_to_new_users_data(users, users_old)

        csv_data = [self._dataframe_to_csv(data) for data in [sfmc_contacts, users]]

        return [data.encode('utf-8', errors='backslashreplace') for data in csv_data]

    def _to_dataframe(self):
        seperators = ['\t', ',', ',', ',']
        encodings_list = ['ISO 8859-1','utf-8','utf-8','utf-8' ]
        return [pandas.read_csv(BytesIO(data), sep=seperator, encoding = encodings, dtype = 'str', low_memory=False) for data, seperator, encodings in zip(self._parameters['data'], seperators, encodings_list)]

    def _assign_id_to_new_sfmc_data(self, sfmc_contacts, sfmc_contacts_old):

        contacts_old_id = self._select_contactid_and_emmpid(sfmc_contacts_old)

        merged_df = self._merge_contacts(sfmc_contacts, contacts_old_id)

        merged_df = self._insert_contactid_column(merged_df)

        merged_df = self._drop_old_contactid_column(merged_df)

        merged_df = self._rename_columns(merged_df)

        merged_df = self._remove_spaces_from_dataframe(merged_df)

        return merged_df

    def _select_contactid_and_emmpid(self, sfmc_contacts_old):
        contacts_old_id = sfmc_contacts_old.loc[:, ['HSContact_ID', 'EMPPID']]

        return contacts_old_id

    def _merge_contacts(self, sfmc_contacts, contacts_old_id):
        merged_df = pd.merge(sfmc_contacts, contacts_old_id, on=['EMPPID'], how='left')

        return merged_df

    def _insert_contactid_column(self, merged_df):
        merged_df.insert(1, 'HSContact_IDD', merged_df.HSContact_ID)

        return merged_df

    def _drop_old_contactid_column(self, merged_df):
        merged_df = merged_df.drop(columns=['HSContact_ID'])

        return merged_df

    def _rename_columns(self, merged_df):
        merged_df.rename(columns={'HSContact_IDD': 'HSContact_ID'}, inplace=True)

        return merged_df

    def _remove_spaces_from_dataframe(self, merged_df):
        merged_df = merged_df.apply(lambda x: x.str.strip())

        return merged_df

    def _assign_id_to_new_users_data(self, users, users_old) :

        users_old = self._drop_columns(users_old)

        users_merged_df = self._merge_users(users, users_old)

        users_merged_df = self._insert_contactid_column(users_merged_df)

        users_merged_df = self._drop_columns_users(users_merged_df)

        users_merged_df = self._rename_column(users_merged_df)

        users_merged_df = self._remove_spaces_users(users_merged_df)

        return users_merged_df

    def _drop_columns(self, users_old):
        users_old.drop(columns=['ADVANTAGE_ID', 'ORG_ISELL_ID'])

        return users_old

    def _merge_users(self, users, users_old):
        users_merged_df = pd.merge(users, users_old,
                                   on=['FIRST_NM', 'LAST_NM', 'EMAIL', 'ORG_NAME', 'ORGANIZATION_TYPE',
                                       'ADDRESS_LINE_1', 'ADDRESS_LINE_2', 'CITY', 'STATE',
                                       'ZIPCODE', 'PHONE_NUMBER', 'TITLE'], how='left')

        return users_merged_df

    def _insert_contactid_column_users(self, users_merged_df):
        users_merged_df.insert(0, 'HSContact_IDD', users_merged_df.HSContact_ID)

        return users_merged_df

    def _drop_columns_users(self, users_merged_df):
        users_merged_df = users_merged_df.drop(columns=['HSContact_ID'])

        return users_merged_df

    def _rename_column(self, users_merged_df):
        users_merged_df.rename(columns={'HSContact_IDD': 'HSContact_ID'}, inplace=True)

        return users_merged_df

    def _remove_spaces_users(self, users_merged_df):
        users_merged_df = users_merged_df.apply(lambda x: x.str.strip())

        return users_merged_df

    @classmethod
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)

