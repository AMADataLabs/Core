""" Oneview PPD Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.iqvia import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIATransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        provider_affiliation_data = data[2]
        iqvia_data = pandas.DataFrame(data[0]['BATCH_BUSINESS_DATE'])[:1]

        primary_keys = [str(column['IMS_ORG_ID']) + str(column['PROFESSIONAL_ID'])
                        for index, column in provider_affiliation_data.iterrows()]
        provider_affiliation_data['id'] = primary_keys
        LOGGER.info(provider_affiliation_data)

        return [data[0], data[1], provider_affiliation_data, iqvia_data]

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS,
                column.PROVIDER_COLUMNS,
                column.PROVIDER_AFFILIATION_COLUMNS,
                column.IQVIA_DATE
                ]
