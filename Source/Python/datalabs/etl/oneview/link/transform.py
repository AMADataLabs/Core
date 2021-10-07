""" OneView Linking Table Transformer"""
import logging
import pandas

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.link.column as columns

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingCustomerBusinessTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        credentialing_customer_business_data = self._link_data(data[0], data[1])

        credentialing_customer_business_data = self._generate_primary_keys(credentialing_customer_business_data)

        return [credentialing_customer_business_data]

    @classmethod
    def _link_data(cls, credentialing_customer_data, business_data):
        credentialing_customer_data = cls._prepare_customer_data_for_merging(credentialing_customer_data)

        matches = pandas.merge(
            credentialing_customer_data,
            business_data,
            left_on=['address_1', 'city', 'state'],
            right_on=['physical_address_1', 'physical_city', 'physical_state'],
            suffixes=['_credentialing', '_business']
        )
        matches = matches[['number', 'id_business']].rename(columns={'id_business': 'id'})

        return matches.drop_duplicates()

    @classmethod
    def _prepare_customer_data_for_merging(cls, credentialing_customer_data):
        credentialing_customer_data = credentialing_customer_data.fillna('None')
        credentialing_customer_data['address_1'] = [x.upper() for x in credentialing_customer_data['address_1']]
        credentialing_customer_data['city'] = [x.upper() for x in credentialing_customer_data['city']]
        credentialing_customer_data['state'] = [x.upper() for x in credentialing_customer_data['state']]

        return credentialing_customer_data

    @classmethod
    def _generate_primary_keys(cls, data):
        data['pk'] = data.number.astype(str) + data.id.astype(str)

        return data

    def _get_columns(self):
        return [columns.CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS]


class CredentialingCustomerInstitutionTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        credentialing_customer_residency_data = self._link_data(data[0], data[1])

        credentialing_customer_residency_data = self._generate_primary_keys(credentialing_customer_residency_data)

        return [credentialing_customer_residency_data]

    @classmethod
    def _link_data(cls, credentialing_customer_data, residency_program_data):
        credentialing_customer_data = credentialing_customer_data.dropna(subset=['address_1', 'city', 'state'],
                                                                         how='all').reset_index()
        residency_program_data = residency_program_data.dropna(subset=['address_1', 'city', 'state'],
                                                               how='all').reset_index()

        matches = pandas.merge(credentialing_customer_data, residency_program_data,
                               left_on=['address_1', 'city'],
                               right_on=['address_3', 'city']
                               )

        return matches[['number', 'institution']]

    @classmethod
    def _generate_primary_keys(cls, data):
        data['pk'] = data.number.astype(str) + data.institution.astype(str)

        return data

    def _get_columns(self):
        return [columns.CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS]


class ResidencyProgramPhysicianTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        linked_residency_physician_data = self._linking_data(data)

        linked_residency_physician_data = self._generate_primary_keys(linked_residency_physician_data)

        return [linked_residency_physician_data]

    @classmethod
    def _linking_data(cls, data):
        directors = cls._get_directors(data[0])
        physicians = cls._get_physicians(data[1])

        directors, unique_directors = cls._find_unique(directors)
        all_match, pure_match = cls._get_matches(physicians, unique_directors)
        duplicate_matches, duplicates = cls._create_duplicate_matches(all_match, pure_match, directors)
        new_match = cls._filter_out_duplicates(duplicates, duplicate_matches)

        return cls._get_all_links(pure_match, new_match, directors)

    @classmethod
    def _get_directors(cls, data):
        directors = data.fillna('None')
        directors['first_name'] = [x.upper().strip() for x in directors.first_name]
        directors['last_name'] = [x.upper().strip() for x in directors.last_name]

        return directors

    @classmethod
    def _get_physicians(cls, physicians):
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
        all_match = pandas.merge(physicians, directors, on=['first_name', 'last_name'], suffixes=('_physician', '_residency'))
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

        if row.degree_1 != 'None' and row.degree_1 != 'MPH':
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

        return pandas.merge(linking_data, directors, on='person_id')[['medical_education_number', 'program']]

    @classmethod
    def _generate_primary_keys(cls, data):
        primary_keys = data['program'].astype(str) + data['medical_education_number'].astype(str)

        data['id'] = primary_keys

        return data

    def _get_columns(self):
        return [columns.RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS]


class CorporateParentBusinessTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        corporate_parent_business = self._link_data(data[0])

        return [corporate_parent_business]

    @classmethod
    def _link_data(cls, business_data):
        has_parent = business_data[business_data['CORP_PARENT_IMS_ORG_ID'].notna()]

        return has_parent[['IMS_ORG_ID', 'CORP_PARENT_IMS_ORG_ID']]

    def _get_columns(self):
        return [columns.CORPORATE_PARENT_BUSINESS]
