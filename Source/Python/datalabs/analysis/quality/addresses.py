""" Addresses transformer for creating Contact entitiy """
# pylint: disable=import-error
from dataclasses import dataclass, fields

import csv
import logging

import pandas

from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class InputData:
    party_address_details: pandas.DataFrame
    medical_education_numbers: pandas.DataFrame
    ppd_party_ids: pandas.DataFrame
    party_post_codes: pandas.DataFrame
    zip_statistics: pandas.DataFrame
    zip_census_details: pandas.DataFrame
    undeliverable_addresses: pandas.DataFrame


class AddressesTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        addresses_entity = self._create_addresses(preprocessed_data)

        postprocessed_data = self._postprocess(addresses_entity)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        return InputData(*[self._csv_to_dataframe(dataset) for dataset in data])

    def _preprocess_data(self, input_data):
        return InputData(*[self._columns_to_lower(getattr(input_data, field.name)) for field in fields(input_data)])

    @classmethod
    def _columns_to_lower(cls, dataset):
        return dataset.rename(columns=lambda x: x.lower())

    def _create_entity(self, preprocessed_data):
        preprocessed_data.all_ids = self._create_oneview_universe(preprocessed_data)

        preprocessed_data.all_addresses = self._merge_universe_party_addresses(preprocessed_data)

        preprocessed_data.all_addresses = self._merge_addresses_post_codes(preprocessed_data)

        preprocessed_data.all_addresses = self._merge_addresses_zip_information(preprocessed_data)

        preprocessed_data.all_addresses = self._merge_addresses_undeliverable_addresses(preprocessed_data)

        return [preprocessed_data.all_addresses]

    @classmethod
    def _create_oneview_universe(cls, preprocessed_data):
        return pandas.merge(
            preprocessed_data.ppd_party_ids,
            preprocessed_data.medical_education_numbers,
            left_on="me",
            right_on="medical_education_numbers",
        ).drop(columns=["me"])

    @classmethod
    def _merge_universe_party_addresses(cls, preprocessed_data):
        return pandas.merge(preprocessed_data.all_ids, preprocessed_data.party_address_details, on="party_id")

    @classmethod
    def _merge_addresses_post_codes(cls, preprocessed_data):
        return pandas.merge(preprocessed_data.all_addresses, preprocessed_data.party_post_codes, on="post_cd_id")

    @classmethod
    def _merge_addresses_zip_information(cls, preprocessed_data):
        preprocessed_data.all_addresses = pandas.merge(
            preprocessed_data.all_addresses,
            preprocessed_data.zip_statistics,
            left_on="post_cd",
            right_on="zip",
            how="left",
        )

        return pandas.merge(
            preprocessed_data.all_addresses,
            preprocessed_data.zip_census_details,
            left_on=["post_cd", "post_cd_plus_4"],
            right_on=["zip_cd", "zip_plus_4"],
            how="left",
        )

    @classmethod
    def _merge_addresses_undeliverable_addresses(cls, preprocessed_data):
        return pandas.merge(
            preprocessed_data.all_addresses, preprocessed_data.undeliverable_addresses, on="comm_id", how="left"
        )

    # pylint: disable=no-self-use
    def _postprocess(self, entities):
        return entities

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
