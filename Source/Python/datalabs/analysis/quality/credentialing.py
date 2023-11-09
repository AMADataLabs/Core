""" Credential transformer for creating Credential entitiy """
from datetime import datetime
import csv
import logging

import pandas

from datalabs.task import Task
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.etl.excel import ExcelReaderMixin
from datalabs.analysis.quality.measurement import MeasurementMethods

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        dataset = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(dataset)

        entities = self._create_entity(preprocessed_data)

        postprocessed_data = self._postprocess(entities)

        return self._pack(postprocessed_data)

    def _parse_input(self, dataset):
        return [self._csv_to_dataframe(data, sep=",") for data in dataset]

    def _preprocess_data(self, dataset):
        preprocessed_data = [self._columns_to_lower(data) for data in dataset]

        return preprocessed_data

    @classmethod
    def _columns_to_lower(cls, data):
        data.rename(columns=lambda x: x.lower(), inplace=True)

        return data

    @classmethod
    def _create_entity(cls, preprocessed_data):
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

        all_licenses = all_licenses.drop_duplicates(["lic_nbr", "degree_cd", "state_id", "party_id"])

        all_dea_registrations = pandas.merge(all_ids, dea_registration, on="party_id").drop_duplicates()

        all_npi_registrations = pandas.merge(all_ids, npi_registration, on="party_id").drop_duplicates()

        return [
            all_ids,
            all_certificates,
            all_licenses,
            all_dea_registrations,
            all_npi_registrations,
        ]

    # pylint: disable=no-self-use
    def _postprocess(self, entities):
        all_ids, all_certificates, *rest = entities

        all_ids.drop(columns=["me"], inplace=True)

        all_certificates.drop(columns=["party_id_from"], inplace=True)

        return [all_ids] + [all_certificates] + rest

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]


class NpiRegistrationCompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        npi_registration_completeness = self._create_npi_registration_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(npi_registration_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        npi_registration_entity, measurement_methods_configurations = data

        npi_registration_entity = self._csv_to_dataframe(npi_registration_entity)

        measurement_methods_configurations = self._excel_to_dataframe(measurement_methods_configurations)

        return [npi_registration_entity, measurement_methods_configurations]

    def _preprocess_data(self, input_data):
        npi_registration_entity, measurement_method_configuration = self._convert_to_lower_case(input_data)

        measurement_method_configuration = self._all_elements_to_lower(measurement_method_configuration)

        npi_registration_entity["enumeration_dt"] = self._reformat_date(npi_registration_entity["enumeration_dt"])

        npi_registration_entity["deactivate_dt"] = self._reformat_date(npi_registration_entity["deactivate_dt"])

        npi_registration_entity["reactivate_dt"] = self._reformat_date(npi_registration_entity["reactivate_dt"])

        return [npi_registration_entity, measurement_method_configuration]

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _reformat_date(cls, data):
        return pandas.to_datetime(data, format="%d-%b-%Y").dt.strftime("%Y-%m-%d")

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_npi_registration_completeness(cls, preprocessed_data):
        npi_registration_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "credentials"
        )

        npi_registration_completeness = measurement_methods.measure_completeness(npi_registration_entity)

        return [npi_registration_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, npi_registration_completeness):
        return npi_registration_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]


class DeaRegistrationCompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        dea_registration_completeness = self._create_dea_registration_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(dea_registration_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        dea_registration_entity, measurement_methods_configurations = data

        dea_registration_entity = self._csv_to_dataframe(dea_registration_entity)

        measurement_methods_configurations = self._excel_to_dataframe(measurement_methods_configurations)

        return [dea_registration_entity, measurement_methods_configurations]

    def _preprocess_data(self, input_data):
        dea_registration_entity, measurement_method_configuration = self._convert_to_lower_case(input_data)

        measurement_method_configuration = self._all_elements_to_lower(measurement_method_configuration)

        dea_registration_entity = self._rename_exp_dt(dea_registration_entity)

        dea_registration_entity["dea_exp_dt"] = self._reformat_date(dea_registration_entity["dea_exp_dt"])

        return [dea_registration_entity, measurement_method_configuration]

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _rename_exp_dt(cls, data):
        return data.rename(columns={"exp_dt": "dea_exp_dt"})

    @classmethod
    def _reformat_date(cls, data):
        return pandas.to_datetime(data, format="%d-%b-%Y").dt.strftime("%Y-%m-%d")

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_dea_registration_completeness(cls, preprocessed_data):
        dea_registration_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "credentials"
        )

        dea_registration_completeness = measurement_methods.measure_completeness(dea_registration_entity)

        return [dea_registration_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, dea_registration_completeness):
        return dea_registration_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]


class LicenseCompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        license_completeness = self._create_license_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(license_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        license_entity, measurement_methods_configurations = data

        license_entity = self._csv_to_dataframe(license_entity)

        measurement_methods_configurations = self._excel_to_dataframe(measurement_methods_configurations)

        return [license_entity, measurement_methods_configurations]

    def _preprocess_data(self, input_data):
        license_entity, measurement_method_configuration = self._convert_to_lower_case(input_data)

        measurement_method_configuration = self._all_elements_to_lower(measurement_method_configuration)

        license_entity = self._rename_exp_dt(license_entity)

        license_entity = self._rename_iss_dt(license_entity)

        # lic_exp_dt and rnw_dt have some date in 2099

        license_entity["lic_exp_dt"] = self._reformat_date(license_entity["lic_exp_dt"])

        license_entity["lic_iss_dt"] = self._reformat_date(license_entity["lic_iss_dt"])

        license_entity["rnw_dt"] = self._reformat_date(license_entity["rnw_dt"])

        return [license_entity, measurement_method_configuration]

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _rename_exp_dt(cls, data):
        return data.rename(columns={"exp_dt": "lic_exp_dt"})

    @classmethod
    def _rename_iss_dt(cls, data):
        return data.rename(columns={"iss_dt": "lic_iss_dt"})

    @classmethod
    def _reformat_date(cls, data):
        return data.apply(lambda x: datetime.strptime(x, "%d-%b-%Y").date() if isinstance(x, str) else x)

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_license_completeness(cls, preprocessed_data):
        license_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "credentials"
        )

        license_completeness = measurement_methods.measure_completeness(license_entity)

        return [license_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, license_completeness):
        return license_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]


class CertificatesCompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        certificates_completeness = self._create_certificates_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(certificates_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        certificates_entity, measurement_methods_configurations = data

        certificates_entity = self._csv_to_dataframe(certificates_entity)

        measurement_methods_configurations = self._excel_to_dataframe(measurement_methods_configurations)

        return [certificates_entity, measurement_methods_configurations]

    def _preprocess_data(self, input_data):
        certificates_entity, measurement_method_configuration = self._convert_to_lower_case(input_data)

        measurement_method_configuration = self._all_elements_to_lower(measurement_method_configuration)

        certificates_entity = self._rename_exp_dt(certificates_entity)

        certificates_entity = self._rename_iss_dt(certificates_entity)

        certificates_entity["certif_exp_dt"] = self._reformat_date(certificates_entity["certif_exp_dt"])

        certificates_entity["certif_iss_dt"] = self._reformat_date(certificates_entity["certif_iss_dt"])

        certificates_entity["reverification_dt"] = self._reformat_date(certificates_entity["reverification_dt"])

        return [certificates_entity, measurement_method_configuration]

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _rename_exp_dt(cls, data):
        return data.rename(columns={"exp_dt": "certif_exp_dt"})

    @classmethod
    def _rename_iss_dt(cls, data):
        return data.rename(columns={"iss_dt": "certif_iss_dt"})

    @classmethod
    def _reformat_date(cls, data):
        return pandas.to_datetime(data, format="%d-%b-%Y").dt.strftime("%Y-%m-%d")

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_certificates_completeness(cls, preprocessed_data):
        certificates_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "credentials"
        )

        certificates_completeness = measurement_methods.measure_completeness(certificates_entity)

        return [certificates_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, certificates_completeness):
        return certificates_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
