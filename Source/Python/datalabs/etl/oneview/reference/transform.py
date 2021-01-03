""" OneView Reference Transformer"""
import logging
import pandas

from   io import StringIO, BytesIO

from   datalabs.etl.oneview.reference.column import MPA_COLUMNS, TOP_COLUMNS, PE_COLUMNS, CBSA_COLUMNS, SPECIALTY_COLUMNS, FIPSC_COLUMNS
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
        self._parameters.data = self._to_dataframe()
        core_based_statistical_area_data = super()._transform()

        return core_based_statistical_area_data

    def _to_dataframe(self):
        return [pandas.read_csv(StringIO(file[1])) for file in self._parameters.data]

    def _get_columns(self):
        return [CBSA_COLUMNS]


class SpecialtyTransformerTask(TransformerTask):
    def _get_columns(self):
        return [SPECIALTY_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    def _transform(self):
        fips_dataframe = self._to_dataframe()
        self._parameters.data = [self.append_column(df) for df in fips_dataframe]
        federal_information_processing_standard_county = super()._transform()

        return federal_information_processing_standard_county

    def _to_dataframe(self):
        return [pandas.read_excel(BytesIO(file[0]), skiprows=4) for file in self._parameters.data]

    @classmethod
    def append_column(cls, dataframe):
        dataframe = dataframe.loc[
            (dataframe['Summary Level'] == 50) |
            (dataframe['Summary Level'] == 40) |
            (dataframe['Summary Level'] == 10)
        ].reset_index(drop=True)

        dataframe['State Code (FIPS)'] = dataframe['State Code (FIPS)'].astype(str)
        dataframe['County Code (FIPS)'] = dataframe['County Code (FIPS)'].astype(str)

        dataframe['FIPS_Code'] = dataframe['State Code (FIPS)'] + dataframe['County Code (FIPS)']

        return dataframe

    def _get_columns(self):
        return [FIPSC_COLUMNS]
