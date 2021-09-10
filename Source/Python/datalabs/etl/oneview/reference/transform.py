""" OneView Reference Transformer"""
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
    def _preprocess_data(self, data):
        filtered_specialty_data = data[0].loc[
            data[0]['SPEC_CD'].isin(data[1]['PRIMSPECIALTY']) | data[0]['SPEC_CD'].isin(data[1]['SECONDARYSPECIALTY'])
        ].reset_index(drop=True)

        return [filtered_specialty_data]

    def _get_columns(self):
        return [SPECIALTY_MERGED_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, path: str, **kwargs):
        return pandas.read_excel(path, skiprows=4, dtype=str, engine='openpyxl', **kwargs)

    def _preprocess_data(self, data):
        fips_selected_data = self.set_columns(data[0])

        primary_keys = [str(column['State Code (FIPS)']) + str(column['County Code (FIPS)'])
                        for index, column in fips_selected_data.iterrows()]
        fips_selected_data['id'] = primary_keys

        return [fips_selected_data]

    @classmethod
    def set_columns(cls, fips_data):
        fips_data = fips_data.loc[
            (fips_data['Summary Level'] == '050') |
            (fips_data['Summary Level'] == '040') |
            (fips_data['Summary Level'] == '010')
        ].reset_index(drop=True)

        return fips_data

    def _get_columns(self):
        return [FIPSC_COLUMNS]

    @classmethod
    def _dataframe_to_csv(cls, data, **kwargs):
        return pandas.DataFrame.to_csv(data).encode()
