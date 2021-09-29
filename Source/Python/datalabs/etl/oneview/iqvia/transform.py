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
        business, provider, provider_affiliation_data = data

        business['class_of_trade_classification_description'] = 'filler'
        provider_affiliation = provider_affiliation_data.merge(provider,
                                                               on='PROFESSIONAL_ID', how='left').drop_duplicates()

        primary_keys = [str(column['IMS_ORG_ID']) + str(column['ME'])
                        for index, column in provider_affiliation.iterrows()]
        provider_affiliation['id'] = primary_keys

        business = self._set_null_values(business)
        return [business, provider, provider_affiliation]

    def _set_null_values(self, business):
        business['COT_SPECIALTY_ID'] = business['COT_SPECIALTY_ID'].fillna(value='-1')
        return business

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS,
                column.PROVIDER_COLUMNS,
                column.PROVIDER_AFFILIATION_COLUMNS,
                ]


class IQVIAUpdateTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        iqvia_update = data[0].iloc[0]['BATCH_BUSINESS_DATE']
        iqvia_update = pandas.DataFrame.from_dict({'BATCH_BUSINESS_DATE': [iqvia_update]})

        return [iqvia_update]

    def _get_columns(self):
        return [column.IQVIA_DATE]
