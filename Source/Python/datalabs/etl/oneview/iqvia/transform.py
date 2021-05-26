""" Oneview PPD Transformer"""
import logging

from   datalabs.etl.oneview.iqvia.column import BUSINESS_COLUMNS, PROVIDER_COLUMNS, PROVIDER_AFFILIATION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIATransformerTask(TransformerTask):
    def _preprocess_data(self, iqvia_data):
        provider_affiliation_data = iqvia_data[2]

        primary_keys = [str(column['IMS_ORG_ID']) + str(column['PROFESSIONAL_ID'])
                        for index, column in provider_affiliation_data.iterrows()]
        provider_affiliation_data['id'] = primary_keys
        LOGGER.info(provider_affiliation_data)

        return [iqvia_data[0], iqvia_data[1], provider_affiliation_data]

    def _get_columns(self):
        return [BUSINESS_COLUMNS, PROVIDER_COLUMNS, PROVIDER_AFFILIATION_COLUMNS]
