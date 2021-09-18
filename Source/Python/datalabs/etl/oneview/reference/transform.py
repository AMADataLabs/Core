""" OneView Reference Transformer"""
import csv
import logging
import pandas

from   datalabs.etl.oneview.reference.column import MPA_COLUMNS, TOP_COLUMNS, PE_COLUMNS, CBSA_COLUMNS,\
    SPECIALTY_MERGED_COLUMNS, FIPSC_COLUMNS, PROVIDER_AFFILIATION_GROUP, PROVIDER_AFFILIATION_TYPE, PROFIT_STATUS, \
    OWNER_STATUS, COT_SPECIALTY, COT_FACILITY, STATE

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.reference.static as tables

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
        return [FIPSC_COLUMNS]


class StaticReferenceTablesTransformerTask(TransformerTask):
    def _transform(self):
        on_disk = bool(self._parameters.get("on_disk") and self._parameters["on_disk"].upper() == 'TRUE')

        table_data = [self._dictionary_to_dataframe(data) for data in [tables.provider_affiliation_group,
                                                                       tables.provider_affiliation_type,
                                                                       tables.profit_status,
                                                                       tables.owner_status]
                      ]

        preprocessed_data = self._preprocess_data(table_data)
        selected_data = self._select_columns(preprocessed_data)
        renamed_data = self._rename_columns(selected_data)
        postprocessed_data = self._postprocess_data(renamed_data)

        return [self._dataframe_to_csv(data, on_disk, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

    @classmethod
    def _dictionary_to_dataframe(cls, data):
        return pandas.DataFrame.from_dict(data)

    def _get_columns(self):
        return [PROVIDER_AFFILIATION_GROUP, PROVIDER_AFFILIATION_TYPE, PROFIT_STATUS, OWNER_STATUS]


class ClassOfTradeTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        class_of_trade_data = data[0]

        specialty_data = class_of_trade_data['COT_SPECIALTY_ID', 'COT_SPECIALTY']
        facility_data = class_of_trade_data['COT_FACILITY_TYPE_ID', 'COT_FACILITY_TYPE']

        return [specialty_data, facility_data]

    def _get_columns(self):
        return [COT_SPECIALTY, COT_FACILITY]

    def _postprocess_data(self, data):
        return [dataframe.drop_duplicates() for dataframe in data]


class StateTransformerTask(TransformerTask):
    def _get_columns(self):
        return [STATE]
