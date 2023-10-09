""" Credential transformer for creating Credential entitiy """
import csv
import logging
import pandas

from   datalabs.task import Task
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ContactTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(data)

        entities = self._create_entity(preprocessed_data)

        postprocessed_data = self._postprocess(entities)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        return [self._csv_to_dataframe(dataset, sep=",") for dataset in data]

    def _preprocess_data(self, data):
        return [self._columns_to_lower(dataset) for dataset in data]

    @classmethod
    def _columns_to_lower(cls, dataset):
        return dataset.rename(columns=lambda x: x.lower())

    def _create_entity(self, preprocessed_data):
        (
            medical_education_number,
            ppd_party_ids,
            zip_statistics,
            zip_census_details,
            party_fax_number,
            party_phone_number,
            party_email_id,
            party_post_codes,
            party_address_details,
            undeliverable_addresses,
        ) = preprocessed_data

        party_address_details["purpose_usg_cd"] = party_address_details["purpose_usg_cd"].str.strip()

        party_phone_number["purpose_usg_cd"] = party_phone_number["purpose_usg_cd"].str.strip()

        party_email_id["purpose_usg_cd"] = party_phone_number["purpose_usg_cd"].str.strip()

        all_ids = pandas.merge(
            ppd_party_ids, medical_education_number, left_on="me", right_on="medical_education_number"
        ).drop(columns=["me"])

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

        preferred_phones = (
            party_phone_number[party_phone_number.purpose_usg_cd == "PV"][["party_id", "phone_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"phone_id": "preferred_phone"})
        )

        party_phones = party_phone_number[["party_id", "phone_id"]].drop_duplicates("party_id")

        party_faxes = (
            party_fax_number[["party_id", "phone_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"phone_id": "fax_id"})
        )

        preferred_emails = (
            party_email_id[party_email_id.purpose_usg_cd == "PE"][["party_id", "email_id"]]
            .drop_duplicates("party_id")
            .rename(columns={"email_id": "preferred_email"})
        )

        party_emails = party_email_id[["party_id", "email_id"]].drop_duplicates("party_id")

        return self._merge_party_entities(
            [
                all_ids,
                party_addresses,
                mailing_addresses,
                office_addresses,
                party_phones,
                preferred_phones,
                party_emails,
                preferred_emails,
                party_faxes,
            ]
        ) + self._merge_comm_entities(
            [
                all_ids,
                party_phone_number,
                party_fax_number,
                party_email_id,
                party_post_codes,
                party_address_details,
                zip_statistics,
                zip_census_details,
                undeliverable_addresses,
            ]
        )

    @classmethod
    def _merge_party_entities(cls, party_level_entities):
        (
            all_ids,
            party_addresses,
            mailing_addresses,
            office_addresses,
            party_phones,
            preferred_phones,
            party_emails,
            preferred_emails,
            party_faxes,
        ) = party_level_entities

        party_level = pandas.merge(all_ids, party_addresses, on="party_id", how="left")

        party_level = pandas.merge(party_level, mailing_addresses, on="party_id", how="left")

        party_level = pandas.merge(party_level, office_addresses, on="party_id", how="left")

        party_level = pandas.merge(party_level, party_phones, on="party_id", how="left")

        party_level = pandas.merge(party_level, preferred_phones, on="party_id", how="left")

        party_level = pandas.merge(party_level, party_emails, on="party_id", how="left")

        party_level = pandas.merge(party_level, preferred_emails, on="party_id", how="left")

        party_level = pandas.merge(party_level, party_faxes, on="party_id", how="left")

        return [party_level]

    @classmethod
    def _merge_comm_entities(cls, comm_entities):
        (
            all_ids,
            party_phone_number,
            party_fax_number,
            party_email_id,
            party_post_codes,
            party_address_details,
            zip_statistics,
            zip_census_details,
            undeliverable_addresses,
        ) = comm_entities

        all_phone_numbers = pandas.merge(all_ids, party_phone_number, on="party_id")

        all_fax_numbers = pandas.merge(all_ids, party_fax_number, on="party_id")

        all_email_ids = pandas.merge(all_ids, party_email_id, on="party_id")

        all_addresses = pandas.merge(all_ids, party_address_details, on="party_id")

        all_addresses = pandas.merge(all_addresses, party_post_codes, on="post_cd_id")

        all_addresses = pandas.merge(all_addresses, zip_statistics, left_on="post_cd", right_on="zip", how="left")

        all_addresses = pandas.merge(
            all_addresses,
            zip_census_details,
            left_on=["post_cd", "post_cd_plus_4"],
            right_on=["zip_cd", "zip_plus_4"],
            how="left",
        )

        all_addresses = pandas.merge(all_addresses, undeliverable_addresses, on="comm_id", how="left")

        return [all_phone_numbers, all_fax_numbers, all_email_ids, all_addresses]

    # pylint: disable=no-self-use
    def _postprocess(self, entities):
        return entities

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
