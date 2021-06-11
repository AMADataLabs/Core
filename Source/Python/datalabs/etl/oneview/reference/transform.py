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
    def _preprocess_data(self, data):
        filtered_specialty_data = data[0].loc[
            data[0]['SPEC_CD'].isin(data[1]['PRIMSPECIALTY']) | data[0]['SPEC_CD'].isin(data[1]['SECONDARYSPECIALTY'])
        ].reset_index(drop=True)

        return [filtered_specialty_data]

    def _get_columns(self):
        return [SPECIALTY_MERGED_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    def _csv_to_dataframe(self, file):
        fips_data = pandas.read_excel(BytesIO(file), skiprows=4)

        return fips_data

    def _preprocess_data(self, data):
        fips_selected_data = self.set_columns(data[0])

        primary_keys = [column['State Code (FIPS)'] + column['County Code (FIPS)']
                        for index, column in fips_selected_data.iterrows()]
        fips_selected_data['id'] = primary_keys

        return [fips_selected_data]

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
