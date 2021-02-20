""" OneView Linking Table Transformer"""
from   io import StringIO

import logging
import pandas

from   datalabs.etl.oneview.link.column import CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS, \
    CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS, RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingCustomerBusinessTransformerTask(TransformerTask):
    def _transform(self):
        credentialing_customer_data, business_data = [self._to_dataframe(csv) for csv in self._parameters['data']]
        self._parameters['data'] = self._link_data(credentialing_customer_data, business_data)

        return [super()._transform()]

    def _get_columns(self):
        return [CREDENTIALING_CUSTOMER_BUSINESS_COLUMNS]

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))

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


class CredentialingCustomerInstitution(TransformerTask):
    def _transform(self):
        credentialing_customer_data, residency_program_data = [self._to_dataframe(csv) for csv in self._parameters['data']]
        self._parameters['data'] = self._link_data(credentialing_customer_data, residency_program_data)

        return [super()._transform()]

    @classmethod
    def _link_data(cls, credentialing_customer_data, residency_program_data):
        matches = pandas.merge(
            credentialing_customer_data, residency_program_data,
            left_on=['address_1', 'city', 'state'],
            right_on=['address_1', 'city', 'state']
        )

        return matches[['number', 'institution']]

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))

    def _get_columns(self):
        return [CREDENTIALING_CUSTOMER_INSTITUTION_COLUMNS]


class ResidencyProgramPhysician(TransformerTask):
    def _transform(self):
        dataframes = [self._to_dataframe(csv) for csv in self._parameters.data]
        self._parameters.data = [self._linking_data(df) for df in dataframes]

        return super()._transform()

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))

    @classmethod
    def _linking_data(cls, data):
        directors = cls._get_directors(data)
        physicians = cls._get_physician(data)

        all_match = pandas.merge(physicians, directors,
                                 on=['first_name', 'last_name'], suffixes=['_physician', '_residency'])
        pure_match = pandas.merge(physicians,
                                  directors,
                                  on=['first_name', 'last_name'],
                                  suffixes=['_ppd', '_residency']).drop_duplicates('aamc_id', keep=False)
        duplicate_matches = all_match[all_match.aamc_id.isin(pure_match.aamc_id) == False]
        duplicates = directors[directors.aamc_id.isin(duplicate_matches.aamc_id)]
        duplicate_matches = duplicate_matches.fillna('None')

        return cls._filter_out_duplicates(pure_match, duplicate_matches, duplicates)

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
    def _filter_out_duplicates(cls, pure_match, duplicate_matches, duplicates):
        matched_dict_list = []
        for row in duplicates.itertuples():
            new_df = duplicate_matches[duplicate_matches.aamc_id == row.aamc_id]
            if row.degree != 'None' and row.degree_one != 'MPH':
                new_df = new_df[new_df.degree == row.degree_one]
            if len(new_df) > 1 and row.middle_name_residency != 'None':
                if len(row.middle_name_residency) == 1:
                    new_df['middle'] = [x[0] for x in new_df.middle_name_physician]
                    new_df = new_df[new_df.middle == row.middle_name_residency]
                else:
                    new_df = new_df[new_df.middle_name_physician == row.middle_name_residency.upper()]
            if len(new_df) == 1:
                matched_dict_list.append({'aamc_id': row.aamc_id,
                                          'medical_education_number': list(new_df.medical_education_number)[0]})

        return pandas.DataFrame(matched_dict_list)

    def _get_columns(self):
        return [RESIDENCY_PROGRAM_PHYSICIAN_COLUMNS]
