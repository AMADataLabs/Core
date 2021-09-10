""" Oneview PPD Transformer"""
import logging
import dask.array
import dask.dataframe

from   datalabs.etl.oneview.iqvia import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIATransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        provider_affiliation_data = data[2]
        provider = data[1]

        primary_keys = dask.array.array([str(column['IMS_ORG_ID']) + str(column['PROFESSIONAL_ID'])
                                         for index, column in provider_affiliation_data.iterrows()])
        provider_affiliation_data['id'] = primary_keys

        provider_affiliation = provider_affiliation_data.merge(provider,
                                                               on='PROFESSIONAL_ID', how='left').drop_duplicates()

        return [data[0], data[1], provider_affiliation]

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS,
                column.PROVIDER_COLUMNS,
                column.PROVIDER_AFFILIATION_COLUMNS,
                ]


class IQVIAUpdateTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        iqvia_data = data[0]
        iqvia_update = iqvia_data['BATCH_BUSINESS_DATE'][0]

        return [iqvia_update]

    def _get_columns(self):
        return [column.IQVIA_DATE]
