""" Oneview PPD Transformer"""
import logging
import pandas

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

        provider_affiliation = provider_affiliation_data.merge(provider,
                                                               on='PROFESSIONAL_ID', how='left').drop_duplicates()

        primary_keys = dask.array.array([str(column['IMS_ORG_ID']) + str(column['ME'])
                                         for index, column in provider_affiliation_data.iterrows()])
        provider_affiliation_data['id'] = primary_keys

        return [data[0], data[1], provider_affiliation]

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS,
                column.PROVIDER_COLUMNS,
                column.PROVIDER_AFFILIATION_COLUMNS,
                ]


class IQVIAUpdateTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        iqvia_update = data[0].compute().iloc[0]['BATCH_BUSINESS_DATE']

        return [pandas.DataFrame.from_dict({'BATCH_BUSINESS_DATE': iqvia_update})]

    def _get_columns(self):
        return [column.IQVIA_DATE]
