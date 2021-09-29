""" OneView Reference Transformer"""
import csv
from   io import BytesIO
import logging

import openpyxl
import pandas

import datalabs.etl.oneview.reference.column as col

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.reference.static as static

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MajorProfessionalActivityTransformerTask(TransformerTask):
    def _get_columns(self):
        return [col.MPA_COLUMNS]


class TypeOfPracticeTransformerTask(TransformerTask):
    def _get_columns(self):
        return [col.TOP_COLUMNS]


class PresentEmploymentTransformerTask(TransformerTask):
    def _get_columns(self):
        return [col.PE_COLUMNS]


class CoreBasedStatisticalAreaTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, data, on_disk):
        cbsa = pandas.read_excel(BytesIO(data))

        codes = cbsa.iloc[2:-4,0]
        titles = cbsa.iloc[2:-4,3]

        return pandas.DataFrame(data={'CBSA Code': codes, 'CBSA Title': titles})

    def _get_columns(self):
        return [col.CBSA_COLUMNS]


class SpecialtyMergeTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        specialties, physicians = data

        filtered_specialty_data = data[0].loc[
            specialties['SPEC_CD'].isin(physicians['primary_specialty']) \
            | specialties['SPEC_CD'].isin(physicians['secondary_specialty'])
        ].reset_index(drop=True)

        return [filtered_specialty_data]

    def _get_columns(self):
        return [col.SPECIALTY_MERGED_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    # pylint: disable=unused-argument
    @classmethod
    def _csv_to_dataframe(cls, data, on_disk, **kwargs):
        return pandas.read_excel(data, skiprows=4, dtype=str, engine='openpyxl', **kwargs)

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
        return [col.FIPSC_COLUMNS]


class StaticReferenceTablesTransformerTask(TransformerTask):
    def _transform(self):
        on_disk = bool(self._parameters.get("on_disk") and self._parameters["on_disk"].upper() == 'TRUE')
        table_data = [pandas.DataFrame.from_dict(table) for table in static.tables]

        preprocessed_data = self._preprocess_data(table_data)
        selected_data = self._select_columns(preprocessed_data)
        renamed_data = self._rename_columns(selected_data)
        postprocessed_data = self._postprocess_data(renamed_data)

        return [self._dataframe_to_csv(data, on_disk, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

    def _get_columns(self):
        return [col.PROVIDER_AFFILIATION_GROUP, col.PROVIDER_AFFILIATION_TYPE, col.PROFIT_STATUS, col.OWNER_STATUS]


class ClassOfTradeTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        class_of_trade_data = data[0]

        classification_data = class_of_trade_data[['CLASSIFICATION_ID', 'CLASSIFICATION']]
        specialty_data = class_of_trade_data[['SPECIALTY_ID', 'SPECIALTY']]
        facility_data = class_of_trade_data[['FACILITY_TYPE_ID', 'FACILITY_TYPE']]

        return [specialty_data, facility_data, classification_data]

    def _postprocess_data(self, data):
        return [dataframe.drop_duplicates() for dataframe in data]

    def _get_columns(self):
        return [col.COT_SPECIALTY, col.COT_FACILITY, col.COT_CLASSIFICATION]


class StateTransformerTask(TransformerTask):
    def _get_columns(self):
        return [col.STATE]


class MedicalSchoolTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        """ TEMPORARY DATA CLEANUP (remove when data source is fixed) """
        medical_schools = data[0]

        cleaned_medical_schools = medical_schools[
            ~(
                (medical_schools.KEY_VAL == '56003') & \
                (medical_schools.ORG_NM == 'Bar-Ilan University Faculty of Medicine in the Galilee')
            )
        ]

        return [cleaned_medical_schools]

    def _get_columns(self):
        return [col.MEDICAL_SCHOOL]
