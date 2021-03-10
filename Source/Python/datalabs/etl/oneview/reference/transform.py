""" OneView Reference Transformer"""
from   io import StringIO, BytesIO

import logging
import pandas

from   datalabs.etl.oneview.reference.column import MPA_COLUMNS, TOP_COLUMNS, PE_COLUMNS, CBSA_COLUMNS, \
    SPECIALTY_COLUMNS, SPECIALTY_MERGED_COLUMNS, FIPSC_COLUMNS
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
    def _transform(self):
        self._parameters['data'] = [self._to_dataframe(file) for file in self._parameters['data']]
        core_based_statistical_area_data = super()._transform()

        return core_based_statistical_area_data.encode('utf-8', errors='backslashreplace')

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(BytesIO(file))

    def _get_columns(self):
        return [CBSA_COLUMNS]


class SpecialtyTransformerTask(TransformerTask):
    def _get_columns(self):
        return [SPECIALTY_COLUMNS]


class SpecialtyMergeTransformerTask(TransformerTask):
    def _transform(self):
        specialty_data, physician_data = [self._to_dataframe(csv) for csv in self._parameters['data']]
        filtered_specialty_data = [
            specialty_data.loc[
                specialty_data.id.isin(physician_data.primary_specialty) |
                specialty_data.id.isin(physician_data.secondary_specialty)
            ].reset_index(drop=True)
        ]

        self._parameters['data'] = filtered_specialty_data

        return [super()._transform()]

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))

    def _get_columns(self):
        return [SPECIALTY_MERGED_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    def _transform(self):
        fips_data = self._to_dataframe()
        self._parameters['data'] = [self.set_columns(df) for df in fips_data]

        return super()._transform()

    def _to_dataframe(self):
        return [pandas.read_excel(BytesIO(file), skiprows=4) for file in self._parameters['data']]

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
