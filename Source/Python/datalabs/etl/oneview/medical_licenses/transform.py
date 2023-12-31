""" Oneview Medical Licenses Transformer"""

import logging

import pandas

from   datalabs.etl.oneview.medical_licenses.column import RAW_MEDICAL_LICENSES_COLUMNS, MEDICAL_LICENSES_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MedicalLicensesCleanerTask(TransformerTask):
    def _postprocess(self, dataset):
        medical_licenses = dataset[0]

        medical_licenses = self._fix_timestamps(medical_licenses)

        medical_licenses = self._standardize_timestamps(medical_licenses)

        return [medical_licenses]

    def _get_columns(self):
        return [RAW_MEDICAL_LICENSES_COLUMNS]

    @classmethod
    def _fix_timestamps(cls, medical_licenses):
        medical_licenses.issue_date = medical_licenses.issue_date.str.replace(
            "(?P<day>[0-3][0-9])-(?P<month>[A-Z][a-z]{2})-(?P<year>02[0-9]{2})",
            lambda m: m.group("day") + "-" + m.group("month") + "-20" + m.group("year")[2:],
            regex=True
        )

        medical_licenses.expiry_date = medical_licenses.expiry_date.str.replace(
            "(?P<day>[0-3][0-9])-(?P<month>[A-Z][a-z]{2})-(?P<year>02[0-9]{2})",
            lambda m: m.group("day") + "-" + m.group("month") + "-20" + m.group("year")[2:],
            regex=True
        )
        medical_licenses.expiry_date = medical_licenses.expiry_date.str.replace(
            "(?P<day>[0-3][0-9])-(?P<month>[A-Z][a-z]{2})-(?P<year>29[0-9][0-9])",
            lambda m: m.group("day") + "-" + m.group("month") + "-" + m.group("year").replace("29", "20"),
            regex=True
        )

        medical_licenses.renew_date = medical_licenses.renew_date.str.replace(
            "(?P<day>[0-3][0-9])-(?P<month>[A-Z][a-z]{2})-(?P<year>02[0-9]{2})",
            lambda m: m.group("day") + "-" + m.group("month") + "-20" + m.group("year")[2:],
            regex=True
        )
        # medical_licenses.issue_date[medical_licenses.issue_date.astype(str).str.endswith("202")]

        return medical_licenses

    @classmethod
    def _standardize_timestamps(cls, medical_licenses):
        medical_licenses.issue_date = pandas.to_datetime(medical_licenses.issue_date).astype(str).replace("NaT", "")
        medical_licenses.expiry_date = pandas.to_datetime(medical_licenses.expiry_date).astype(str).replace("NaT", "")
        medical_licenses.renew_date = pandas.to_datetime(medical_licenses.renew_date).astype(str).replace("NaT", "")

        return medical_licenses


class MedicalLicensesTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        medical_licenses, party_keys, physicians = dataset

        supplemented_medical_licenses = self._supplement_with_medical_education_numbers(medical_licenses, party_keys)

        pruned_medical_licences = self._prune_medical_licenses(supplemented_medical_licenses, physicians)

        return [pruned_medical_licences]

    def _postprocess(self, dataset):
        medical_licenses = dataset[0]

        medical_licenses['id'] = self._generate_primary_keys(medical_licenses)

        return [medical_licenses]

    @classmethod
    def _supplement_with_medical_education_numbers(cls, medical_licenses, party_keys):
        party_keys = party_keys[['PARTY_ID', 'meNumber']]
        medical_licenses_me = medical_licenses.merge(party_keys, on='PARTY_ID', how="left").drop_duplicates()

        return medical_licenses_me

    @classmethod
    def _prune_medical_licenses(cls, licenses, physicians):
        licenses = licenses[(licenses.meNumber.isin(physicians.medical_education_number))]

        return licenses.drop_duplicates()

    @classmethod
    def _generate_primary_keys(cls, medical_licenses):
        degree_types = medical_licenses.degree_type.fillna('')

        return medical_licenses.number + medical_licenses.state + degree_types

    def _get_columns(self):
        return [MEDICAL_LICENSES_COLUMNS]
