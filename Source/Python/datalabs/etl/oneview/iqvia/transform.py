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
        provider_affiliation = provider_affiliation_data.merge(
            provider,
            on='PROFESSIONAL_ID', how='left'
        ).drop_duplicates()

        business, provider_affiliation = self._set_null_values(business, provider_affiliation)
        business = self._set_unaccounted_values(business)

        provider_affiliation['id'] = data.IMS_ORG_ID.astype(str) + data.ME.astype(str)

        return [business, provider, provider_affiliation]

    @classmethod
    def _set_null_values(cls, business, provider_affiliation):
        business['COT_SPECIALTY_ID'] = business['COT_SPECIALTY_ID'].fillna(value='-1')

        business['PROFIT_STATUS'] = business['PROFIT_STATUS'].fillna(value='UNKNOWN')
        business['OWNER_STATUS'] = business['OWNER_STATUS'].fillna(value='UNKNOWN')

        provider_affiliation['AFFIL_TYPE_ID'] = provider_affiliation['AFFIL_TYPE_ID'].fillna(value=0)
        provider_affiliation['AFFIL_GROUP_CODE'] = provider_affiliation['AFFIL_GROUP_CODE'].fillna(value='UNKNOWN')

        provider_affiliation = provider_affiliation[provider_affiliation['ME'].notna()]

        return business, provider_affiliation

    @classmethod
    def _set_unaccounted_values(cls, business):
        business['COT_CLASSIFICATION_ID'] = business['COT_CLASSIFICATION_ID'].replace(['24'], '-1')

        business['COT_FACILITY_TYPE_ID'] = business['COT_FACILITY_TYPE_ID'].astype(str).replace(
            ['69', '70', '75', '76', '52', '53', '54', '59', '63'],
            '-1'
        )

        business['COT_SPECIALTY_ID'] = business['COT_SPECIALTY_ID'].astype(str).replace('.0', '', regex=True)
        business['COT_SPECIALTY_ID'] = business['COT_SPECIALTY_ID'].replace(
            ['0', '1', '2', '4', '5', '6', '7', '8', '9', '229', '129', '224', '231', ],
            '-1'
        )

        return business

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS, column.PROVIDER_COLUMNS, column.PROVIDER_AFFILIATION_COLUMNS]


class IQVIAUpdateTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        iqvia_update = data[0].iloc[0]['BATCH_BUSINESS_DATE']
        iqvia_update = pandas.DataFrame.from_dict({'BATCH_BUSINESS_DATE': [iqvia_update]})

        return [iqvia_update]

    def _get_columns(self):
        return [column.IQVIA_DATE]
