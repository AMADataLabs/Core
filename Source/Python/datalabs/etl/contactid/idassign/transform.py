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
        contacts_old_id = sfmc_contacts_old.loc[:, ['HSContact_ID', 'EMPPID']]
        merged_df = pd.merge(sfmc_contacts, contacts_old_id, on=['EMPPID'], how='left')
        merged_df.insert(1, 'HSContact_IDD', merged_df.HSContact_ID)
        merged_df = merged_df.drop(columns=['HSContact_ID'])
        merged_df.rename(columns={'HSContact_IDD': 'HSContact_ID'}, inplace=True)

        return merged_df

    def _assign_id_to_new_users_data(self, users, users_old) :
        users_old = users_old.drop(columns=['ADVANTAGE_ID', 'ORG_ISELL_ID'])
        users_merged_df = pd.merge(users, users_old,
                                   on=['FIRST_NM', 'LAST_NM', 'EMAIL', 'ORG_NAME', 'ORGANIZATION_TYPE',
                                       'ADDRESS_LINE_1', 'ADDRESS_LINE_2', 'CITY', 'STATE',
                                       'ZIPCODE', 'PHONE_NUMBER', 'TITLE'], how='left')
        users_merged_df.insert(0, 'HSContact_IDD', users_merged_df.HSContact_ID)
        users_merged_df = users_merged_df.drop(columns=['HSContact_ID'])
        users_merged_df.rename(columns={'HSContact_IDD': 'HSContact_ID'}, inplace=True)

        return users_merged_df

    @classmethod
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)

