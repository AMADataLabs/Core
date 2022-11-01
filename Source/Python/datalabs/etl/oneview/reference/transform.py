""" OneView Reference Transformer"""
import csv
from   io import BytesIO
import logging

import pandas

from   datalabs.etl.oneview.reference import static, column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MajorProfessionalActivityTransformerTask(TransformerTask):
    def _get_columns(self):
        return [column.MPA_COLUMNS]


class TypeOfPracticeTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        type_of_practice = dataset[0]

        type_of_practice = type_of_practice.append(
            pandas.DataFrame(
                data={
                    'TOP_CD': ['000'],
                    'DESC': ['Student']
                }
            )
        )

        type_of_practice = type_of_practice[type_of_practice.TOP_CD != '070']

        return [type_of_practice]

    def _get_columns(self):
        return [column.TOP_COLUMNS]


class PresentEmploymentTransformerTask(TransformerTask):
    def _get_columns(self):
        return [column.PE_COLUMNS]


class CoreBasedStatisticalAreaTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, data, **kwargs):
        cbsa = pandas.read_excel(BytesIO(data))

        codes = cbsa.iloc[2:-4, 0]
        titles = cbsa.iloc[2:-4, 3]

        table = pandas.DataFrame(data={'CBSA Code': codes, 'CBSA Title': titles}).drop_duplicates()
        table = table.append({'CBSA Code': '00000', 'CBSA Title': 'Unknown/Not Specified'}, ignore_index=True)

        return table

    def _get_columns(self):
        return [column.CBSA_COLUMNS]


class SpecialtyMergeTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        specialties, physicians = dataset

        specialties.SPEC_CD = specialties.SPEC_CD = specialties.SPEC_CD.str.strip()

        filtered_specialty_data = specialties.loc[
            specialties['SPEC_CD'].isin(physicians['primary_specialty']) \
            | specialties['SPEC_CD'].isin(physicians['secondary_specialty'])
        ].reset_index(drop=True)

        return [filtered_specialty_data]

    def _get_columns(self):
        return [column.SPECIALTY_MERGED_COLUMNS]


class FederalInformationProcessingStandardCountyTransformerTask(TransformerTask):
    # pylint: disable=unused-argument
    @classmethod
    def _csv_to_dataframe(cls, data, **kwargs):
        page_tables = pandas.read_html(data, converters={'FIPS': str}, **kwargs)

        return page_tables[1]

    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        fips = dataset[0]

        fips['state'] = fips.FIPS.str[:2]
        fips['county'] = fips.FIPS.str[2:]
        fips['description'] = fips[['County or equivalent', 'State or equivalent']].apply(
            lambda row: ', '.join(row.values),
            axis=1
        )
        fips.description = fips.description.str.replace(r'\[.\]', '')

        return [fips]

    def _get_columns(self):
        return [column.FIPSC_COLUMNS]


class StaticReferenceTablesTransformerTask(TransformerTask):
    def run(self):
        table_data = [pandas.DataFrame.from_dict(table) for table in static.tables]

        preprocessed_data = self._preprocess(table_data)
        selected_data = self._select_columns(preprocessed_data)
        renamed_data = self._rename_columns(selected_data)
        postprocessed_data = self._postprocess(renamed_data)

        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

    def _get_columns(self):
        return [
            column.PROVIDER_AFFILIATION_GROUP,
            column.PROVIDER_AFFILIATION_TYPE,
            column.PROFIT_STATUS,
            column.OWNER_STATUS
        ]


class ClassOfTradeTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        class_of_trade = dataset[0]

        specialties = self._add_specialty_defaults(class_of_trade[['SPECIALTY_ID', 'SPECIALTY']])

        facilities = self._add_facility_defaults(class_of_trade[['FACILITY_TYPE_ID', 'FACILITY_TYPE']])

        classifications = self._add_classification_defaults(class_of_trade[['CLASSIFICATION_ID', 'CLASSIFICATION']])

        return [specialties, facilities, classifications]

    def _postprocess(self, dataset):
        return [dataframe.drop_duplicates() for dataframe in dataset]

    def _get_columns(self):
        return [column.COT_SPECIALTY, column.COT_FACILITY, column.COT_CLASSIFICATION]

    @classmethod
    def _add_classification_defaults(cls, classifications):
        classifications = classifications.append(
            pandas.DataFrame(
                data={'CLASSIFICATION_ID': ['-1', '24'], 'CLASSIFICATION': ['Unknown/Not Specified', 'Other']})
        )

        return classifications

    @classmethod
    def _add_facility_defaults(cls, facilities):
        facilities = facilities.append(
            pandas.DataFrame(
                data={'FACILITY_TYPE_ID': ['52', '53', '54', '59', '63', '69', '70', '75', '76', '78'],
                      'FACILITY_TYPE': ['Other Supply', 'Warehouse', 'Wholesaler', 'Other Government', 'Other Pharmacy',
                                        'Distributor - Medical/Surgical Supply', 'Distributor - Pharmaceutical Supply',
                                        'Internet', 'Non-Retail Pharmacy', 'Support Services']}
            )
        )

        facilities = facilities.append(
            pandas.DataFrame(
                data={'FACILITY_TYPE_ID': ['-1'], 'FACILITY_TYPE': ['Unknown/Not Specified']})
        )

        return facilities

    @classmethod
    def _add_specialty_defaults(cls, specialties):
        specialties.SPECIALTY[specialties.SPECIALTY_ID == '-1'] = 'Unknown/Not Specified'

        specialties = specialties.append(
            pandas.DataFrame(
                data={'SPECIALTY_ID': ['129', '219', '224', '229', '231'],
                      'SPECIALTY': ['Hemophilia Treatment Center', 'Other', 'Epilepsy', 'Chain', 'Mail Service']}
            )
        )

        return specialties


class StateTransformerTask(TransformerTask):
    def _get_columns(self):
        return [column.STATE]


class MedicalSchoolTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        """ TEMPORARY DATA CLEANUP (remove when data source is fixed) """
        medical_schools = dataset[0]

        cleaned_medical_schools = medical_schools[
            ~(
                    (medical_schools.KEY_VAL == '56003') & \
                    (medical_schools.ORG_NM == 'Bar-Ilan University Faculty of Medicine in the Galilee')
            )
        ]

        return [cleaned_medical_schools]

    def _get_columns(self):
        return [column.MEDICAL_SCHOOL]
