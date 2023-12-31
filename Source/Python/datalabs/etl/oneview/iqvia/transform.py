""" Oneview PPD Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.iqvia import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIABusinessTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        business, class_of_trade = dataset
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
        class_of_trade_classification = class_of_trade.CLASSIFICATION_ID.to_list()
        class_of_trade_classification.extend(['24'])
        business.COT_CLASSIFICATION_ID[~business.COT_CLASSIFICATION_ID.isin(class_of_trade_classification)] = '-1'

        class_of_trade_facility = class_of_trade.FACILITY_TYPE_ID.to_list()
        class_of_trade_facility.extend(['52', '53', '54', '59', '63', '69', '70', '75', '76', '78'])
        business.COT_FACILITY_TYPE_ID[~business.COT_FACILITY_TYPE_ID.isin(class_of_trade_facility)] = '-1'

        class_of_trade_specialty = class_of_trade.SPECIALTY_ID.to_list()
        class_of_trade_specialty.extend(['129', '219', '224', '229', '231'])
        business.COT_SPECIALTY_ID = [data.rstrip("0").rstrip('.') for data in business.COT_SPECIALTY_ID]
        business.COT_SPECIALTY_ID[~business.COT_SPECIALTY_ID.isin(class_of_trade_specialty)] = '-1'

        return business

    def _postprocess(self, dataset):
        business = dataset[0]

        business["physical_zipcode5"] = business.physical_zipcode.str[:5]

        return [business]

    def _get_columns(self):
        return [column.BUSINESS_COLUMNS]


class IQVIAProviderTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        providers, affiliations, best_affiliations = dataset

        affiliations = affiliations.merge(
            providers,
            on='PROFESSIONAL_ID', how='left'
        ).drop_duplicates()

        affiliations = self._set_default_values(affiliations)
        affiliations = self._clean(affiliations)
        affiliations = self._match_best_affiliation(affiliations, best_affiliations)

        return [providers, affiliations]

    @classmethod
    def _set_default_values(cls, affiliations):
        affiliations['AFFIL_TYPE_ID'] = affiliations['AFFIL_TYPE_ID'].fillna(value=0)

        affiliations['AFFIL_GROUP_CODE'] = affiliations['AFFIL_GROUP_CODE'].fillna(value='UNKNOWN')

        affiliations = affiliations[affiliations['ME'].notna()]

        affiliations['id'] = affiliations.IMS_ORG_ID.astype(str) + affiliations.ME.astype(str)

        return affiliations

    @classmethod
    def _clean(cls, affiliations):
        row_data = []
        for row in affiliations.AFFIL_GROUP_CODE.to_list():
            row_data.append(row.rstrip())

        affiliations['AFFIL_GROUP_CODE'] = row_data

        return affiliations

    @classmethod
    def _match_best_affiliation(cls, affiliations, best_affiliations):
        best_affiliations['BEST'] = True

        affiliations = pandas.merge(affiliations, best_affiliations, on=["IMS_ORG_ID", "PROFESSIONAL_ID"], how="left")

        affiliations = affiliations.drop(columns=column.PROVIDER_BEST_AFFILIATION_DROPPED_COLUMNS)

        affiliations = affiliations.rename(columns=column.PROVIDER_BEST_AFFILIATION_COLUMNS)

        affiliations['BEST'] = affiliations['BEST'].fillna(False)

        return affiliations

    def _get_columns(self):
        return [column.PROVIDER_COLUMNS, column.PROVIDER_AFFILIATION_COLUMNS]


class IQVIAProviderPruningTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        providers, affiliations, physicians = dataset

        physicians['truncated_me'] = physicians.medical_education_number.apply(lambda me: me[:-1])
        providers.rename(columns=dict(medical_education_number='truncated_me'), inplace=True)
        affiliations.rename(columns=dict(medical_education_number='truncated_me'), inplace=True)

        providers = providers[
            providers.truncated_me.isin(physicians.truncated_me)
        ]
        providers = providers.merge(
            physicians[['medical_education_number', 'truncated_me']],
            on='truncated_me', how='left'
        ).drop_duplicates()

        affiliations = affiliations[
            affiliations.truncated_me.isin(physicians.truncated_me)
        ]
        affiliations = affiliations.merge(
            physicians[['medical_education_number', 'truncated_me']],
            on='truncated_me', how='left'
        ).drop_duplicates()

        return [providers, affiliations]

    def _get_columns(self):
        provider_columns = {value: value for value in column.PROVIDER_COLUMNS.values()}
        affiliation_columns = {value: value for value in column.PROVIDER_AFFILIATION_COLUMNS.values()}

        return [provider_columns, affiliation_columns]


class IQVIAUpdateTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        iqvia_update = dataset[0].iloc[0]['BATCH_BUSINESS_DATE']
        iqvia_update = pandas.DataFrame.from_dict({'BATCH_BUSINESS_DATE': [iqvia_update]})

        iqvia_update.BATCH_BUSINESS_DATE = pandas.to_datetime(iqvia_update.BATCH_BUSINESS_DATE).astype(str)

        return [iqvia_update]

    def _get_columns(self):
        return [column.IQVIA_DATE]
