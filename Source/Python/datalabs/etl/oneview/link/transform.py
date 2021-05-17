""" OneView Linking Table Transformer"""
from   io import BytesIO

import logging
import pandas

from   datalabs.etl.oneview.link.column import CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS
from   datalabs.etl.oneview.link.column import CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingCustomerBusinessTransformerTask(TransformerTask):
    def _to_dataframe(self):
        credentialing_customer_business_data = [pandas.read_csv(BytesIO(csv)) for csv in self._parameters['data']]
        credentialing_customer_business_data = self._link_data(credentialing_customer_business_data[0],
                                                               credentialing_customer_business_data[1])
        primary_keys = [column['number'] + column['id']
                        for index, column in credentialing_customer_business_data.iterrows()]
        credentialing_customer_business_data['pk'] = primary_keys

        return [credentialing_customer_business_data]

    @classmethod
    def _link_data(cls, credentialing_customer_data, business_data):
        credentialing_customer_data = cls._prepare_customer_data_for_merging(credentialing_customer_data)

        matches = pandas.merge(
            credentialing_customer_data,
            business_data,
            left_on=['address_1', 'city', 'state'],
            right_on=['physical_address_1', 'physical_city', 'physical_state']
        )

        return matches[['number', 'id']]

    @classmethod
    def _prepare_customer_data_for_merging(cls, credentialing_customer_data):
        credentialing_customer_data = credentialing_customer_data.fillna('None')
        credentialing_customer_data['address_1'] = [x.upper() for x in credentialing_customer_data['address_1']]
        credentialing_customer_data['city'] = [x.upper() for x in credentialing_customer_data['city']]
        credentialing_customer_data['state'] = [x.upper() for x in credentialing_customer_data['state']]

        return credentialing_customer_data

    def _get_columns(self):
        return [CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS]


class CredentialingCustomerInstitution(TransformerTask):
    def _to_dataframe(self):
        credentialing_customer_residency_data = [pandas.read_csv(BytesIO(csv)) for csv in self._parameters['data']]
        credentialing_customer_residency_data = self._link_data(credentialing_customer_residency_data[0],
                                                                credentialing_customer_residency_data[1])

        primary_keys = [column['number'] + column['institution']
                        for index, column in credentialing_customer_residency_data.iterrows()]
        credentialing_customer_residency_data['pk'] = primary_keys

        return [credentialing_customer_residency_data]

    @classmethod
    def _link_data(cls, credentialing_customer_data, residency_program_data):
        matches = pandas.merge(
            credentialing_customer_data, residency_program_data,
            left_on=['address_1', 'city', 'state'],
            right_on=['address_1', 'city', 'state']
        )

        return matches[['number', 'institution']]

    def _get_columns(self):
        return [CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS]
