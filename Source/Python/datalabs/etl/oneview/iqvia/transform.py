""" Oneview PPD Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.iqvia import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIABusinessTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        business, class_of_trade = data

        business = self._set_default_values(business)

        business = self._replace_unknown_values(business, class_of_trade)

        return [business]

    @classmethod
    def _set_default_values(cls, business):
        business['COT_SPECIALTY_ID'] = business['COT_SPECIALTY_ID'].fillna(value='-1')

        business['PROFIT_STATUS'] = business['PROFIT_STATUS'].fillna(value='UNKNOWN')

        business['OWNER_STATUS'] = business['OWNER_STATUS'].fillna(value='UNKNOWN')

        return business

    @classmethod
    def _replace_unknown_values(cls, business, class_of_trade):
        business.COT_CLASSIFICATION_ID[~business.COT_CLASSIFICATION_ID.isin(class_of_trade.CLASSIFICATION_ID)] = '-1'

        business.COT_FACILITY_TYPE_ID[~business.COT_FACILITY_TYPE_ID.isin(class_of_trade.FACILITY_TYPE_ID)] = '-1'

        business.COT_SPECIALTY_ID[~business.COT_SPECIALTY_ID.isin(class_of_trade.SPECIALTY_ID)] = '-1'

        return business

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS]


class IQVIAProviderTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        providers, affiliations = data

        affiliations = affiliations.merge(
            providers,
            on='PROFESSIONAL_ID', how='left'
        ).drop_duplicates()

        affiliations = self._set_default_values(affiliations)
        affiliations = self._clean_data(affiliations)

        return [providers, affiliations]

    @classmethod
    def _set_default_values(cls, affiliations):
        affiliations['AFFIL_TYPE_ID'] = affiliations['AFFIL_TYPE_ID'].fillna(value=0)

        affiliations['AFFIL_GROUP_CODE'] = affiliations['AFFIL_GROUP_CODE'].fillna(value='UNKNOWN')

        affiliations = affiliations[affiliations['ME'].notna()]

        affiliations['id'] = affiliations.IMS_ORG_ID.astype(str) + affiliations.ME.astype(str)

        return affiliations

    @classmethod
    def _clean_data(cls, affiliations):
        row_data = []
        for row in affiliations.AFFIL_GROUP_CODE.to_list():
            row_data.append(row.rstrip())

        affiliations['AFFIL_GROUP_CODE'] = row_data

        return affiliations

    def _get_columns(self):
        return [column.PROVIDER_COLUMNS, column.PROVIDER_AFFILIATION_COLUMNS]


class IQVIAProviderPruningTransformerTask(TransformerTask):
    @classmethod
    def _preprocess_data(cls, data):
        providers, affiliations, physicians = data
        physicians['truncated_me'] = physicians.medical_education_number.apply(lambda me: me[:-1])
        providers.rename(columns=dict(medical_education_number='truncated_me'), inplace=True)
        affiliations.rename(columns=dict(medical_education_number='truncated_me'), inplace=True)

        providers = providers[
            providers.truncated_me.isin(physicians.truncated_me)
        ]
        providers = providers.merge(
            physicians[['medical_education_number', 'truncated_me']],
            on='truncated_me', how='left'
        ).drop_duplicates

        affiliations = affiliations[
            affiliations.truncated_me.isin(physicians.truncated_me)
        ]
        affiliations = affiliations.merge(
            physicians[['medical_education_number', 'truncated_me']],
            on='truncated_me', how='left'
        )

        return [providers, affiliations]

    def _get_columns(self):
        provider_columns = {value:value for value in column.PROVIDER_COLUMNS.values()}
        affiliation_columns = {value:value for value in column.PROVIDER_AFFILIATION_COLUMNS.values()}

        return [provider_columns, affiliation_columns]


class IQVIAUpdateTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        iqvia_update = data[0].iloc[0]['batch_business_date']
        iqvia_update = pandas.DataFrame.from_dict({'batch_business_date': [iqvia_update]})

        return [iqvia_update]

    def _get_columns(self):
        return [column.IQVIA_DATE]
