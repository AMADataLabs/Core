""" Practice transformer class for creating Practice entitiy """
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


class PracticeTransformerTask(Task, CSVReaderMixin, CSVWriterMixin):
    def run(self):
        dataset = self._parse_input(self._data)

        preprocessed_data = self._preprocess(dataset)

        entity = self._create_entity(preprocessed_data)

        postprocessed_data = self._postprocess(entity)

        return self._pack(postprocessed_data)

    def _parse_input(self, dataset):
        return [self._csv_to_dataframe(data, sep=",") for data in dataset]

    def _preprocess(self, dataset):
        dataset = [self._convert_columns_to_lower_case(data) for data in dataset]

        return dataset

    @classmethod
    def _convert_columns_to_lower_case(cls, data):
        data.rename(columns=lambda x: x.lower(), inplace=True)

        return data

    # pylint: disable=no-self-use
    def _create_entity(self, preprocessed_data):
        (
            medical_education_number,
            ppd_party_ids,
            employer_ids,
            active_mpa_codes,
            specialities,
            pra_certifications,
        ) = preprocessed_data

        pra_certifications.expiration_dt = pandas.to_datetime(pra_certifications.expiration_dt)

        current_certifications = (
            pra_certifications[pra_certifications.expiration_dt > datetime.today()]
            .sort_values("expiration_dt")
            .drop_duplicates("party_id", keep="last")
        )

        entity = pandas.merge(
            ppd_party_ids,
            medical_education_number,
            left_on="me",
            right_on="medical_education_number",
        )

        entity = pandas.merge(entity, employer_ids, on="party_id", how="left")

        entity = pandas.merge(
            entity,
            specialities[specialities.prefe_lvl == "1"],
            on="party_id",
            how="left",
        )

        entity = pandas.merge(
            entity,
            specialities[specialities.prefe_lvl == "2"],
            on="party_id",
            suffixes=["_prim", "_sec"],
            how="left",
        )

        entity = pandas.merge(entity, active_mpa_codes, on=["top_id", "employer_id"], how="left")

        entity = pandas.merge(entity, current_certifications, on="party_id", how="left")

        return [entity]

    # pylint: disable=no-self-use
    def _postprocess(self, entity):
        entity[0].drop(columns=["me"], inplace=True)

        return entity

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]


class CompletenessTransformerTask(Task, CSVReaderMixin, CSVWriterMixin, ExcelReaderMixin, MeasurementMethods):
    def run(self):
        input_data = self._parse_input(self._data)

        preprocessed_data = self._preprocess_data(input_data)

        practice_completeness = self._create_practice_completeness(preprocessed_data)

        postprocessed_data = self._postprocess(practice_completeness)

        return self._pack(postprocessed_data)

    def _parse_input(self, data):
        practice_entity, measurement_methods = data

        practice_entity = self._csv_to_dataframe(practice_entity)

        measurement_methods = self._excel_to_dataframe(measurement_methods)

        return [practice_entity, measurement_methods]

    def _preprocess_data(self, input_data):
        practice_entity, measurement_method_configuration = self._convert_to_lower_case(input_data)

        measurement_method_configuration = self._all_elements_to_lower(measurement_method_configuration)

        return [practice_entity, measurement_method_configuration]

    @classmethod
    def _all_elements_to_lower(cls, data):
        return data.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    @classmethod
    def _convert_to_lower_case(cls, data):
        return [dataset.rename(columns=lambda x: x.lower()) for dataset in data]

    @classmethod
    def _create_practice_completeness(cls, preprocessed_data):
        practice_entity, measurement_methods_configuration = preprocessed_data

        measurement_methods = MeasurementMethods.create_measurement_methods(
            measurement_methods_configuration, "completeness", "practice"
        )

        practice_completeness = measurement_methods.measure_completeness(practice_entity)

        return [practice_completeness]

    # pylint: disable=no-self-use
    def _postprocess(self, practice_completeness):
        return practice_completeness

    def _pack(self, postprocessed_data):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]
