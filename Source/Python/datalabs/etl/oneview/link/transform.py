""" OneView Linking Table Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.link.column as columns

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingCustomerBusinessTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        customers, businesses = dataset

        customer_businesses = self._link_customers_to_businesses(customers, businesses)

        customer_businesses = self._generate_primary_keys(customer_businesses)

        return [customer_businesses]

    @classmethod
    def _link_customers_to_businesses(cls, customers, businesses):
        customers = cls._prepare_customer_data_for_merging(customers)

        customer_businesses = pandas.merge(
            customers,
            businesses,
            left_on=['address_1', 'city', 'state'],
            right_on=['physical_address_1', 'physical_city', 'physical_state'],
            suffixes=['_credentialing', '_business']
        )
        customer_businesses = customer_businesses[['number', 'id_business']].rename(columns={'id_business': 'id'})

        return customer_businesses.drop_duplicates()

    @classmethod
    def _prepare_customer_data_for_merging(cls, customers):
        customers = customers.fillna('None')

        customers['address_1'] = [x.upper() for x in customers['address_1']]
        customers['city'] = [x.upper() for x in customers['city']]
        customers['state'] = [x.upper() for x in customers['state']]

        return customers

    @classmethod
    def _generate_primary_keys(cls, data):
        data['pk'] = data.number.astype(str) + data.id.astype(str)

        return data

    def _get_columns(self):
        return [columns.CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS]


class CredentialingCustomerInstitutionTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        customers, residency_programs = dataset

        customer_residency_programs = self._link_customers_to_residency_programs(customers, residency_programs)

        customer_residency_programs = self._generate_primary_keys(customer_residency_programs)

        return [customer_residency_programs]

    @classmethod
    def _link_customers_to_residency_programs(cls, customers, residency_programs):
        customers = customers.dropna(
            subset=['address_1', 'city', 'state'],
            how='all'
        ).reset_index()

        residency_programs = residency_programs.dropna(
            subset=['address_1', 'city', 'state'],
            how='all'
        ).reset_index()

        customer_residency_programs = pandas.merge(
            customers,
            residency_programs,
            left_on=['address_1', 'city'],
            right_on=['address_3', 'city']
        )

        return customer_residency_programs[['number', 'institution']]

    @classmethod
    def _generate_primary_keys(cls, data):
        data['pk'] = data.number.astype(str) + data.institution.astype(str)

        return data

    def _get_columns(self):
        return [columns.CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS]


class ResidencyProgramPhysicianTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        directors, physicians = dataset

        directors = self._clean_directors(directors)

        physicians = self._clean_physicians(physicians)

        director_physicians = self._link_directors_with_physicians(directors, physicians)

        director_physicians = self._generate_primary_keys(director_physicians)

        return [director_physicians]

    @classmethod
    def _link_directors_with_physicians(cls, directors, physicians):
        directors, unique_directors = cls._find_unique(directors)

        all_match, pure_match = cls._get_matches(physicians, unique_directors)

        duplicate_matches, duplicates = cls._create_duplicate_matches(all_match, pure_match, directors)

        new_match = cls._filter_out_duplicates(duplicates, duplicate_matches)

        return cls._get_all_links(pure_match, new_match, directors)

    @classmethod
    def _clean_directors(cls, directors):
        directors = directors.fillna('None')
        directors['first_name'] = [x.upper().strip() for x in directors.first_name]
        directors['last_name'] = [x.upper().strip() for x in directors.last_name]

        return directors

    @classmethod
    def _clean_physicians(cls, physicians):
        physicians['degree_1'] = ['MD' if x == 1 else 'DO' for x in physicians.degree_type]
        physicians['first_name'] = [str(x).upper().strip() for x in physicians.first_name]
        physicians['last_name'] = [str(x).upper().strip() for x in physicians.last_name]

        return physicians

    @classmethod
    def _find_unique(cls, directors):
        identifying_fields = ['last_name', 'first_name', 'middle_name', 'degree_1', 'degree_2', 'degree_3']
        unique_directors = directors.drop_duplicates(identifying_fields).sort_values('last_name')
        unique_directors = unique_directors[identifying_fields]
        unique_directors['person_id'] = list(range(len(unique_directors)))
        directors = pandas.merge(directors, unique_directors, on=identifying_fields)

        return directors, unique_directors

    @classmethod
    def _get_matches(cls, physicians, directors):
        all_match = pandas.merge(
            physicians,
            directors, on=['first_name', 'last_name'], suffixes=('_physician', '_residency')
        )
        pure_match = pandas.merge(physicians, directors, on=[
            'first_name', 'last_name'], suffixes=('_physician', '_residency')).drop_duplicates('person_id', keep=False)

        return all_match, pure_match

    @classmethod
    def _create_duplicate_matches(cls, all_match, pure_match, directors):
        duplicate_matches = all_match[~all_match.person_id.isin(pure_match.person_id)]
        duplicates = directors[directors.person_id.isin(duplicate_matches.person_id)]
        duplicate_matches = duplicate_matches.fillna('None')

        return duplicate_matches, duplicates

    @classmethod
    def _filter_out_duplicates(cls, duplicates, duplicate_matches):
        matched_dict_list = []

        for row in duplicates.itertuples():
            new_df = cls._merge_filtered_dataframe(row, duplicate_matches)
            if len(new_df) == 1:
                matched_dict_list.append(
                    {'person_id': row.person_id, 'medical_education_number': list(new_df.medical_education_number)[0]})

        return pandas.DataFrame(matched_dict_list)

    @classmethod
    def _merge_filtered_dataframe(cls, row, duplicate_matches):
        new_df = duplicate_matches[duplicate_matches.person_id == row.person_id]

        if row.degree_1 not in ('None', 'MPH'):
            new_df = new_df[new_df.degree_1_physician == row.degree_1]

        if len(new_df) > 1 and row.middle_name != 'None':
            if len(row.middle_name) == 1:
                new_df['middle'] = [x[0] for x in new_df.middle_name_physician]
                new_df = new_df[new_df.middle == row.middle_name]
            else:
                new_df = new_df[new_df.middle_name_physician == row.middle_name.upper()]

        return new_df

    @classmethod
    def _get_all_links(cls, pure_match, new_match, directors):
        linking_data = pandas.concat([pure_match[['medical_education_number', 'person_id']], new_match])

        return pandas.merge(linking_data, directors, on='person_id')[[
            'medical_education_number',
            'program'
        ]].drop_duplicates(ignore_index=True)

    @classmethod
    def _generate_primary_keys(cls, data):
        primary_keys = data['program'].astype(str) + data['medical_education_number'].astype(str)

        data['pk'] = primary_keys

        return data

    def _get_columns(self):
        return [columns.RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS]


class CorporateParentBusinessTransformerTask(TransformerTask):
    def _preprocess(self, dataset):
        businesses = dataset[0]

        corporate_parent_businesses = self._link_corporate_parents_to_businesses(businesses)

        return [corporate_parent_businesses]

    @classmethod
    def _link_corporate_parents_to_businesses(cls, businesses):
        corporate_parent_businesses = businesses[businesses['CORP_PARENT_IMS_ORG_ID'].notna()]

        return corporate_parent_businesses[['IMS_ORG_ID', 'CORP_PARENT_IMS_ORG_ID']]

    def _get_columns(self):
        return [columns.CORPORATE_PARENT_BUSINESS]
