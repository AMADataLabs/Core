""" Oneview Medical Licenses Transformer"""

import logging

from   datalabs.etl.oneview.medical_licenses.column import MEDICAL_LICENSES_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MedicalLicensesTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        medical_licenses, party_keys, physicians = data

        appended_medical_licenses = self.generate_medical_education_number(medical_licenses, party_keys)
        pruned_medical_licences = self.prune_medical_licenses(appended_medical_licenses, physicians)

        return [pruned_medical_licences]

    @classmethod
    def generate_medical_education_number(cls, medical_licenses, party_keys):
        party_keys = party_keys[['PARTY_ID', 'meNumber']]
        medical_licenses_me = medical_licenses.merge(party_keys, on='PARTY_ID', how="left").drop_duplicates()
        medical_licenses_me = medical_licenses_me.drop('PARTY_ID', axis=1)

        return medical_licenses_me

    @classmethod
    def prune_medical_licenses(cls, licenses, physicians):
        licenses = licenses[(licenses.meNumber.isin(physicians.medical_education_number))]
        return licenses.drop_duplicates()

    def _get_columns(self):
        return [MEDICAL_LICENSES_COLUMNS]
