""" OneView Reference Transformer"""
import csv
from   io import BytesIO
import logging

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
    def _preprocess_data(self, data):
        type_of_practice = data[0]

        type_of_practice = type_of_practice.append(
            pandas.DataFrame(
                data={'TOP_CD': ['000'],
                      'DESC': ['Student']}
            )
        )

        type_of_practice = type_of_practice[type_of_practice.TOP_CD != '070']

        return [type_of_practice]

    def _get_columns(self):
        return [col.TOP_COLUMNS]


class PresentEmploymentTransformerTask(TransformerTask):
    def _get_columns(self):
        return [col.PE_COLUMNS]


class CoreBasedStatisticalAreaTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, data, on_disk, **kwargs):
        cbsa = pandas.read_excel(BytesIO(data))

        codes = cbsa.iloc[2:-4, 0]
        titles = cbsa.iloc[2:-4, 3]

        table = pandas.DataFrame(data={'CBSA Code': codes, 'CBSA Title': titles}).drop_duplicates()
        table = table.append({'CBSA Code': '00000', 'CBSA Title': 'Unknown/Not Specified'}, ignore_index=True)

        return table

    def _get_columns(self):
        return [col.CBSA_COLUMNS]


class SpecialtyMergeTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        specialties, physicians = data

        specialties.SPEC_CD = specialties.SPEC_CD = specialties.SPEC_CD.str.strip()

        filtered_specialty_data = specialties.loc[
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
        page_tables = pandas.read_html(data, converters={'FIPS': str}, **kwargs)

        return page_tables[1]

    def _preprocess_data(self, data):
        fips = data[0]
        fips['state'] = fips.FIPS.str[:2]
        fips['county'] = fips.FIPS.str[2:]
        fips['description'] = fips[['County or equivalent', 'State or equivalent']].apply(
            lambda row: ', '.join(row.values),
            axis=1
        )
        fips.description = fips.description.str.replace(r'\[.\]', '')

        return [fips]

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
    @classmethod
    def _preprocess_data(cls, data):
        classification_data = cls._add_classification_defaults(data[0][['CLASSIFICATION_ID', 'CLASSIFICATION']])

        facility_data = cls._add_facility_defaults(data[0][['FACILITY_TYPE_ID', 'FACILITY_TYPE']])

        specialty_data = cls._add_specialty_defaults(data[0][['SPECIALTY_ID', 'SPECIALTY']])

        return [specialty_data, facility_data, classification_data]

    def _postprocess_data(self, data):
        return [dataframe.drop_duplicates() for dataframe in data]

    def _get_columns(self):
        return [col.COT_SPECIALTY, col.COT_FACILITY, col.COT_CLASSIFICATION]

    @classmethod
    def _add_classification_defaults(cls, classification_data):
        classification_data = classification_data.append(
            pandas.DataFrame(
                data={'CLASSIFICATION_ID': ['-1', '24'], 'CLASSIFICATION': ['Unknown/Not Specified', 'Other']})
        )

        return classification_data

    @classmethod
    def _add_facility_defaults(cls, facility_data):
        facility_data = facility_data.append(
            pandas.DataFrame(
                data={'FACILITY_TYPE_ID': ['52', '53', '54', '59', '63', '69', '70', '75', '76', '78'],
                      'FACILITY_TYPE': ['Other Supply', 'Warehouse', 'Wholesaler', 'Other Government', 'Other Pharmacy',
                                        'Distributor - Medical/Surgical Supply', 'Distributor - Pharmaceutical Supply',
                                        'Internet', 'Non-Retail Pharmacy', 'Support Services']}
            )
        )
        facility_data = facility_data.append(
            pandas.DataFrame(
                data={'FACILITY_TYPE_ID': ['-1'], 'FACILITY_TYPE': ['Unknown/Not Specified']})
        )

        return facility_data

    @classmethod
    def _add_specialty_defaults(cls, specialty_data):
        specialty_data.SPECIALTY[specialty_data.SPECIALTY_ID == '-1'] = 'Unknown/Not Specified'

        specialty_data = specialty_data.append(
            pandas.DataFrame(
                data={'SPECIALTY_ID': ['129', '219', '224', '229', '231'],
                      'SPECIALTY': ['Hemophilia Treatment Center', 'Other', 'Epilepsy', 'Chain', 'Mail Service']}
            )
        )

        return specialty_data


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
