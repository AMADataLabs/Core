""" OneView Linking Table Transformer"""
from   io import BytesIO

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
            right_on=['physical_address_1', 'physical_city', 'physical_state']
        )

        return matches[['number', 'id']]

    @classmethod
    def _prepare_customer_data_for_merging(cls, credentialing_customer_data):
        credentialing_customer_data = credentialing_customer_data.fillna('None')
        credentialing_customer_data['address_1'] = [x.upper() for x in credentialing_customer_data['address_1']]
        credentialing_customer_data['city'] = [x.upper() for x in credentialing_customer_data['city']]
        credentialing_customer_data['state'] = [x.upper() for x in credentialing_customer_data['state']]

        return credentialing_customer_data

    @classmethod
    def _generate_primary_keys(cls, data):
        primary_keys = [column['number'] + column['id']
                        for index, column in data.iterrows()]
        data['pk'] = primary_keys

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
        matches = pandas.merge(
            credentialing_customer_data, residency_program_data,
            left_on=['address_1', 'city', 'state'],
            right_on=['address_1', 'city', 'state']
        )

        return matches[['number', 'institution']]

    @classmethod
    def _generate_primary_keys(cls, data):
        primary_keys = [column['number'] + column['institution']
                        for index, column in data.iterrows()]
        data['pk'] = primary_keys

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
        directors = cls._get_directors(data)
        physicians = cls._get_physician(data)

        all_match, pure_match = cls._get_matches(physicians, directors)
        duplicate_matches, duplicates = cls._create_duplicate_matches(all_match, pure_match, directors)

        return cls._filter_out_duplicates(duplicate_matches, duplicates)

    @classmethod
    def _get_matches(cls, physicians, directors):
        all_match = pandas.merge(physicians, directors,
                                 on=['first_name', 'last_name'], suffixes=['_physician', '_residency'])
        pure_match = pandas.merge(physicians,
                                  directors,
                                  on=['first_name', 'last_name'],
                                  suffixes=['_ppd', '_residency']).drop_duplicates('aamc_id', keep=False)

        return all_match, pure_match

    @classmethod
    def _create_duplicate_matches(cls, all_match, pure_match, directors):
        duplicate_matches = all_match[~all_match.aamc_id.isin(pure_match.aamc_id)]
        duplicates = directors[directors.aamc_id.isin(duplicate_matches.aamc_id)]
        duplicate_matches = duplicate_matches.fillna('None')

        return duplicate_matches, duplicates

    @classmethod
    def _get_directors(cls, data):
        data[0] = data[0].fillna('None')
        data[0]['first_name'] = [x.upper() for x in data[0].first_name]
        data[0]['last_name'] = [x.upper() for x in data[0].last_name]
        data[0] = data[0][data[0].aamc_id != 'None'].sort_values(
            ['survey_cycle']).drop_duplicates(['aamc_id'], keep='last')

        return data[0]

    @classmethod
    def _get_physician(cls, data):
        data[1]['degree'] = ['MD' if x == 1 else 'DO' for x in data[1].degree_type]

        return data[1]

    @classmethod
    def _filter_out_duplicates(cls, duplicate_matches, duplicates):
        matched_dict_list = []
        for row in duplicates.itertuples():
            new_df = cls._merge_filtered_dataframe(row, duplicate_matches)

            if len(new_df) == 1:
                matched_dict_list.append({'aamc_id': row.aamc_id,
                                          'medical_education_number': list(new_df.medical_education_number)[0]})

        return pandas.DataFrame(matched_dict_list)

    @classmethod
    def _merge_filtered_dataframe(cls, row, duplicate_matches):
        new_df = duplicate_matches[duplicate_matches.aamc_id == row.aamc_id]

        if row.degree != 'None' and row.degree_one != 'MPH':
            new_df = new_df[new_df.degree == row.degree_one]

        if len(new_df) > 1 and row.middle_name_residency != 'None':
            if len(row.middle_name_residency) == 1:
                new_df['middle'] = [x[0] for x in new_df.middle_name_physician]
                new_df = new_df[new_df.middle == row.middle_name_residency]
            else:
                new_df = new_df[new_df.middle_name_physician == row.middle_name_residency.upper()]

        return new_df

    @classmethod
    def _generate_primary_keys(cls, data):
        primary_keys = [column['personnel_member'] + column['medical_education_number']
                        for index, column in data.iterrows()]
        data['pk'] = primary_keys

        return data

    def _get_columns(self):
        return [columns.RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS]
