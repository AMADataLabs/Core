""" Person transformer class for creating Person entitiy """
from dataclasses import dataclass, fields
import csv
import logging
import json

import pandas

from datalabs.task import Task
from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.etl.excel import ExcelReaderMixin
from datalabs.analysis.quality.measurement import MeasurementMethods

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class InputData:
    race_ethnicities: pandas.DataFrame
    medical_education_numbers: pandas.DataFrame
    person_types: pandas.DataFrame
    party_ids: pandas.DataFrame
    entity_ids: pandas.DataFrame
    person_details: pandas.DataFrame
    person_names: pandas.DataFrame


class PersonTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    def run(self):
        metadata = self._parse_metadata(self._parameters["METADATA"])

        input_data = self._parse_input(self._data, metadata)

        preprocessed_data = self._preprocess_data(input_data)

        person_entity = self._create_person_entity(preprocessed_data)

        postprocessed_data = self._postprocess(person_entity)

        return self._pack(postprocessed_data)

    # pylint: disable=no-self-use
    def _parse_metadata(self, metadata):
        json_metadata = json.loads(metadata)

        return {
            list(rows[1].keys())[0]: {"index": rows[0], "seperator": list(rows[1].values())[0]}
            for rows in enumerate(json_metadata)
        }

    def _parse_input(self, data, metadata):
        return InputData(*[self._csv_to_dataframe(data[i["index"]], sep=i["seperator"]) for i in metadata.values()])

    def _preprocess_data(self, input_data):
        return InputData(
            *[self._columns_to_lower_case(getattr(input_data, field.name)) for field in fields(input_data)]
        )

    @classmethod
    def _columns_to_lower_case(cls, dataset):
        return dataset.rename(columns=lambda x: x.lower())

    def _create_person_entity(self, preprocessed_data):
        preprocessed_data.all_ids = self._merge_entity_party_ids(preprocessed_data)

        preprocessed_data.person_data = self._create_person_universe(preprocessed_data)

        preprocessed_data.person_data = self._merge_person_race_ethnicities(preprocessed_data)

        preprocessed_data.person_data = self._merge_person_information(preprocessed_data)

        return [preprocessed_data.person_data]

    @classmethod
    def _merge_entity_party_ids(cls, preprocessed_data):
        return pandas.merge(preprocessed_data.entity_ids, preprocessed_data.party_ids, on="party_id")

    @classmethod
    def _create_person_universe(cls, preprocessed_data):
        return pandas.merge(
            preprocessed_data.all_ids,
            preprocessed_data.medical_education_numbers,
            left_on="me",
            right_on="medical_education_number",
            how="right",
        )

    @classmethod
    def _merge_person_race_ethnicities(cls, preprocessed_data):
        return pandas.merge(
            preprocessed_data.person_data, preprocessed_data.race_ethnicities, on="medical_education_number", how="left"
        )

    @classmethod
    def _merge_person_information(cls, preprocessed_data):
        preprocessed_data.person_data = pandas.merge(
            preprocessed_data.person_data, preprocessed_data.person_types, on="entity_id", how="left"
        ).drop_duplicates()

        preprocessed_data.person_data = pandas.merge(
            preprocessed_data.person_data, preprocessed_data.person_names, on="party_id", how="left"
        ).drop_duplicates()

        return pandas.merge(
            preprocessed_data.person_data, preprocessed_data.person_details, on="party_id", how="left"
        ).drop_duplicates()

    def _postprocess(self, person_entity):
        return [person_entity[0].drop(columns=["me", "med_edu_nbr"])]

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]


class CompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        person_completeness = self._create_person_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(person_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        person_entity, measurement_methods_configuration = data

        person_entity = self._csv_to_dataframe(person_entity)

        measurement_methods_configuration = self._excel_to_dataframe(measurement_methods_configuration)

        return [person_entity, measurement_methods_configuration]

    def _preprocess_data(self, input_data):
        person_entity, measurement_methods_configuration = self._convert_to_lower_case(input_data)

        person_entity["birth_country_id"] = self._replacing_zeros(person_entity["birth_country_id"])

        person_entity["birth_state_id"] = self._replacing_zeros(person_entity["birth_state_id"])

        measurement_methods_configuration = self._all_elements_to_lower(measurement_methods_configuration)

        return [person_entity, measurement_methods_configuration]

    @classmethod
    def _replacing_zeros(cls, data):
        return data.apply(lambda x: str(x).replace(".0", ""))

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_person_completeness(cls, preprocessed_data):
        person_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "person"
        )

        person_completeness = measurement_methods.measure_completeness(person_entity)

        return [person_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, person_completeness):
        return person_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
