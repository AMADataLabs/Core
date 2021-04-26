""" OneView Reference Transformer"""
from   io import BytesIO

import logging
import pandas

from   datalabs.etl.oneview.reference.column import MPA_COLUMNS, TOP_COLUMNS, PE_COLUMNS, CBSA_COLUMNS, \
    SPECIALTY_MERGED_COLUMNS, FIPSC_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MajorProfessionalActivityTransformerTask(TransformerTask):
    def _get_columns(self):
        return [MPA_COLUMNS]


class TypeOfPracticeTransformerTask(TransformerTask):
    def _get_columns(self):
        return [TOP_COLUMNS]


class PresentEmploymentTransformerTask(TransformerTask):
    def _get_columns(self):
        return [PE_COLUMNS]


class CoreBasedStatisticalAreaTransformerTask(TransformerTask):
    def _get_columns(self):
        return [CBSA_COLUMNS]


class SpecialtyMergeTransformerTask(TransformerTask):
    def _to_dataframe(self):
        specialty_physician_data = [pandas.read_csv(BytesIO(csv)) for csv in self._parameters['data']]
        filtered_specialty_data = [
            specialty_physician_data[0].loc[
                specialty_physician_data[0]['SPEC_CD'].isin(specialty_physician_data[1]['PRIMSPECIALTY']) |
                specialty_physician_data[0]['SPEC_CD'].isin(specialty_physician_data[1]['SECONDARYSPECIALTY'])
            ].reset_index(drop=True)
        ]

        return filtered_specialty_data

    def _get_columns(self):
        return [SPECIALTY_MERGED_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    def _to_dataframe(self):
        fips_data = [pandas.read_excel(BytesIO(data), skiprows=4) for data in self._parameters['data']]
        return [self.set_columns(df) for df in fips_data]

    @classmethod
    def set_columns(cls, fips_data):
        fips_data = fips_data.loc[
            (fips_data['Summary Level'] == 50) |
            (fips_data['Summary Level'] == 40) |
            (fips_data['Summary Level'] == 10)
        ].reset_index(drop=True)

        return fips_data

    def _get_columns(self):
        return [FIPSC_COLUMNS]
