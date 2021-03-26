from   abc import ABC, abstractmethod
from   io import BytesIO

import csv
import logging
import pandas
import numpy as np
import uuid

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class ContactIDMergeTransformerTask(etl.TransformerTask, ABC):
    def _transform(self):
        LOGGER.info(self._parameters['data'])

        sfmc_contacts, api_orders, active_subscription, users = self._to_dataframe()

        sfmc_contacts = self._assign_id_to_contacts(sfmc_contacts)

        #users = self._assign_id_to_users(users, sfmc_contacts)

        LOGGER.info(sfmc_contacts.head(2))

        csv_data = [self._dataframe_to_csv(data) for data in [sfmc_contacts, api_orders, active_subscription, users]]

        return [data.encode('utf-8', errors='backslashreplace') for data in csv_data]

    def _to_dataframe(self):
        seperators = ['\t', ',', ',', ',']
        encodings = ['ISO 8859-1','utf-8','utf-8','utf-8']
        return [pandas.read_csv(BytesIO(data), sep=seperator, encoding = encodings) for data, seperator, encodings in zip(self._parameters['data'], seperators, encodings)]

    def _assign_id_to_contacts(self, sfmc_contacts):
        sfmc_contacts["HSContact_ID"] = np.nan
        emppid = -1
        for index in sfmc_contacts.index:
            if (sfmc_contacts['EMPPID'][index] != emppid):
                id = uuid.uuid1()
                sfmc_contacts['HSContact_ID'][index] = id.int
            else:
                prev_index = index - 1
                sfmc_contacts['HSContact_ID'][index] = sfmc_contacts['HSContact_ID'][prev_index]
            emppid = sfmc_contacts['EMPPID'][index]

        return sfmc_contacts
    
    @classmethod
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)
'''
    def _assign_id_to_users(users, sfmc_contacts):
        users['HSContact_ID'] = np.nan
        for index_users in users.index:
            for index_contacts in sfmc_contacts.index:
            if users['FIRS_NM'][index_users] in sfmc_contacts['PARSE_FIRST'][index_contacts]:
                if users['LAST_NM'][index_users] in sfmc_contacts['PARSE_LAST'][index_contacts]:
                    if users['EMAIL'][index_users] in sfmc_contacts['EMAIL_ADDRESS'][index_contacts]:
                        users['HSContact_ID'][index_users] = sfmc_contacts['HSContact_ID'][index_contacts]
            else:
                id = uuid.uuid1()
                users['HSContact_ID'][index_users]
                sfmc_contacts = sfmc_contacts.append({'HSContact_ID':id.int})
                sfmc_contacts = sfmc_contacts.append({'NAME': users['FIRS_NM'] + users['LAST_NM]})
                sfmc_contacts = sfmc_contacts.append({'EMAIL_ADDRESS': users['EMAIL']})
        for index in users.index:
            if users['HSContact_ID'] == 'Nan':
                id = uuid.uuid1()
                users['HSContact_ID'][index] = id.int
'''

