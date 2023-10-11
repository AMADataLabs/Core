""" Coomunications transformer for creating Contact entitiy """
# pylint: disable=import-error
from dataclasses import dataclass, fields

import csv
import logging

# pylint: disable=wrong-import-order
import pandas

from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class InputData:
    party_address_details: pandas.DataFrame
    party_phone_numbers: pandas.DataFrame
    party_email_ids: pandas.DataFrame
    medical_education_numbers: pandas.DataFrame
    ppd_party_ids: pandas.DataFrame
    party_fax_numbers: pandas.DataFrame


class CommunicationsTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        communication_entities = self._create_communication_entities(preprocessed_data)

        postprocessed_data = self._postprocess(communication_entities)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        return InputData(*[self._csv_to_dataframe(dataset) for dataset in data])

    def _preprocess_data(self, input_data):
        input_data = InputData(
            *[self._columns_to_lower(getattr(input_data, field.name)) for field in fields(input_data)]
        )

        input_data = self._strip_purpose_usage_code(input_data)

        return input_data

    @classmethod
    def _strip_purpose_usage_code(cls, input_data):
        input_data.party_address_details["purpose_usg_cd"] = input_data.party_address_details["purpose_usg_cd"].apply(
            lambda x: x.strip()
        )

        input_data.party_phone_numbers["purpose_usg_cd"] = input_data.party_phone_numbers["purpose_usg_cd"].apply(
            lambda x: x.strip()
        )

        input_data.party_email_ids["purpose_usg_cd"] = input_data.party_email_ids["purpose_usg_cd"].apply(
            lambda x: x.strip()
        )

        return input_data

    @classmethod
    def _columns_to_lower(cls, dataset):
        return dataset.rename(columns=lambda x: x.lower())

    def _create_communication_entities(self, preprocessed_data):
        (
            preprocessed_data.office_addresses,
            preprocessed_data.mailing_addresses,
            preprocessed_data.party_addresses,
        ) = self._get_address_types(preprocessed_data.party_address_details)

        preprocessed_data.preferred_phones, preprocessed_data.party_phones = self._get_phone_types(
            preprocessed_data.party_phone_numbers
        )

        preprocessed_data.preferred_emails, preprocessed_data.party_emails = self._get_email_types(
            preprocessed_data.party_email_ids
        )

        preprocessed_data.party_faxes = self._get_fax_types(preprocessed_data.party_fax_numbers)

        preprocessed_data.all_ids = self._oneview_universe(
            preprocessed_data.ppd_party_ids,
            preprocessed_data.medical_education_numbers,
        )

        return self._merge_party_entities(preprocessed_data) + self._merge_communication_entites(preprocessed_data)

    @classmethod
    def _get_address_types(cls, party_address_details):
        office_addresses = (
            party_address_details[party_address_details.purpose_usg_cd == "PO"][["party_id", "post_cd_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"post_cd_id": "polo_address"})
        )

        mailing_addresses = (
            party_address_details[party_address_details.purpose_usg_cd == "PP"][["party_id", "post_cd_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"post_cd_id": "ppma_address"})
        )

        party_addresses = (
            party_address_details[["party_id", "post_cd_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"post_cd_id": "address"})
        )

        return [office_addresses, mailing_addresses, party_addresses]

    @classmethod
    def _get_phone_types(cls, party_phone_number):
        preferred_phones = (
            party_phone_number[party_phone_number.purpose_usg_cd == "PV"][["party_id", "phone_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"phone_id": "preferred_phone"})
        )

        party_phones = party_phone_number[["party_id", "phone_id"]].drop_duplicates("party_id")

        return [preferred_phones, party_phones]

    @classmethod
    def _get_email_types(cls, party_email_id):
        preferred_emails = (
            party_email_id[party_email_id.purpose_usg_cd == "PE"][["party_id", "email_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"email_id": "preferred_email"})
        )

        party_emails = party_email_id[["party_id", "email_id"]].drop_duplicates("party_id")

        return [preferred_emails, party_emails]

    @classmethod
    def _get_fax_types(cls, party_fax_number):
        return (
            party_fax_number[["party_id", "phone_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"phone_id": "fax_id"})
        )

    @classmethod
    def _oneview_universe(cls, ppd_party_ids, medical_education_numbers):
        return pandas.merge(
            ppd_party_ids,
            medical_education_numbers,
            left_on="me",
            right_on="medical_education_numbers",
        ).drop(columns=["me"])

    @classmethod
    def _merge_party_entities(cls, preprocessed_data):
        preprocessed_data.party_level = cls._merge_party_address_entities(preprocessed_data)

        preprocessed_data.party_level = cls._merge_party_phone_entities(preprocessed_data)

        preprocessed_data.party_level = cls._merge_party_email_entities(preprocessed_data)

        preprocessed_data.party_level = cls._merge_party_fax_entities(preprocessed_data)

        return [preprocessed_data.party_level]

    @classmethod
    def _merge_party_address_entities(cls, preprocessed_data):
        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.all_ids, preprocessed_data.party_addresses, on="party_id", how="left"
        )

        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.mailing_addresses, on="party_id", how="left"
        )

        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.office_addresses, on="party_id", how="left"
        )

        return preprocessed_data.party_level

    @classmethod
    def _merge_party_phone_entities(cls, preprocessed_data):
        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.party_phones, on="party_id", how="left"
        )

        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.preferred_phones, on="party_id", how="left"
        )

        return preprocessed_data.party_level

    @classmethod
    def _merge_party_email_entities(cls, preprocessed_data):
        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.party_emails, on="party_id", how="left"
        )

        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.preferred_emails, on="party_id", how="left"
        )

        return preprocessed_data.party_level

    @classmethod
    def _merge_party_fax_entities(cls, preprocessed_data):
        preprocessed_data.party_level = pandas.merge(
            preprocessed_data.party_level, preprocessed_data.party_faxes, on="party_id", how="left"
        )

        return preprocessed_data.party_level

    @classmethod
    def _merge_communication_entites(cls, preprocessed_data):
        preprocessed_data.all_phone_numbers = pandas.merge(
            preprocessed_data.all_ids, preprocessed_data.party_phone_numbers, on="party_id"
        )

        preprocessed_data.all_fax_numbers = pandas.merge(
            preprocessed_data.all_ids, preprocessed_data.party_fax_numbers, on="party_id"
        )

        preprocessed_data.all_email_ids = pandas.merge(
            preprocessed_data.all_ids, preprocessed_data.party_email_ids, on="party_id"
        )

        return [preprocessed_data.all_phone_numbers, preprocessed_data.all_fax_numbers, preprocessed_data.all_email_ids]

    # pylint: disable=no-self-use
    def _postprocess(self, entities):
        return entities

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

