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

        LOGGER.info(sfmc_contacts.head(2))

        csv_data = [self._dataframe_to_csv(data) for data in [sfmc_contacts, api_orders, active_subscription, users]]

        return [data.encode('utf-8', errors='backslashreplace') for data in csv_data]

    def _to_dataframe(self):
        return [pandas.read_csv(BytesIO(file)) for file in self._parameters['data']]

    def _assign_id_to_contacts(self, sfmc_contacts):
        sfmc_contacts["HSContactID"] = np.nan
        emppid = -1
        for index in sfmc_contacts.index:
            if (sfmc_contacts['EMPPID'][index] != emppid):
                id = uuid.uuid1()
                sfmc_contacts['HSContactID'][index] = id.int
            else:
                prev_index = index - 1
                sfmc_contacts['HSContactID'][index] = sfmc_contacts['HSContactID'][prev_index]
            emppid = (sfmc_contacts['HSContactID'][index]



    @classmethod
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)
