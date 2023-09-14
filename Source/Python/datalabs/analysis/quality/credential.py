""" Credential transformer for creating Credential entitiy """
# pylint: disable=import-error
import csv
import logging
import pandas

# pylint: disable=wrong-import-order
from datalabs.task import Task
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        dataset = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(dataset)

        created_entities = self._create_entity(preprocessed_data)

        postprocessed_data = self._postprocess(created_entities)

        return self._pack(postprocessed_data)

    def _parse_input(self, dataset):
        return [self._csv_to_dataframe(data, sep=",") for data in dataset]

    def _preprocess_data(self, dataset):
        preprocessed_data = [self._columns_to_lower(data) for data in dataset]

        return preprocessed_data

    def _columns_to_lower(self, data):
        data.rename(columns=lambda x: x.lower(), inplace=True)

        return data

    def _create_entity(self, preprocessed_data):
        (
            medical_education_number,
            ppd_party_ids,
            certificates,
            licenses,
            dea_registration,
            npi_registration,
        ) = preprocessed_data

        all_ids = pandas.merge(
            ppd_party_ids,
            medical_education_number,
            left_on="me",
            right_on="medical_education_number",
        )
        all_certificates = pandas.merge(
            all_ids, certificates, left_on="party_id", right_on="party_id_from"
        ).drop_duplicates("certif_id")

        all_licenses = pandas.merge(all_ids, licenses, on="party_id").drop_duplicates()

        all_licenses = all_licenses.drop_duplicates(
            ["lic_nbr", "degree_cd", "state_id", "party_id"]
        )

        all_dea_registrations = pandas.merge(
            all_ids, dea_registration, on="party_id"
        ).drop_duplicates()

        all_npi_registrations = pandas.merge(
            all_ids, npi_registration, on="party_id"
        ).drop_duplicates()

        return [
            all_ids,
            all_certificates,
            all_licenses,
            all_dea_registrations,
            all_npi_registrations,
        ]

    # pylint: disable=no-self-use
    def _postprocess(self, created_entities):
        all_ids, all_certificates, *rest = created_entities
        all_ids.drop(columns=["me"], inplace=True)
        all_certificates.drop(columns=["party_id_from"], inplace=True)

        return [all_ids] + [all_certificates] + rest

    def _pack(self, postprocessed_data):
        return [
            self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC)
            for data in postprocessed_data
        ]
