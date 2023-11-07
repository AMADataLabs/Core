""" Measurement  """
# pylint: disable=wrong-import-order
from datetime import datetime

import logging
import pandas
import re

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MeasurementMethods:
    def __init__(self) -> None:
        self._measure = pandas.DataFrame()

    @classmethod
    def _measurement_methods_reformatting(cls, rows):
        if isinstance(rows["condition_value"], str):
            rows["condition_value"] = rows["condition_value"].split(" ")
        else:
            rows["condition_value"] = [rows["condition_value"]]
        if isinstance(rows["value"], str):
            if re.compile(r"\d{1,2}/\d{1,2}/\d{4}").match(rows["value"]):
                rows["value"] = [datetime.strptime(rows["value"], "%m/%d/%Y").strftime("%Y-%m-%d")]
            else:
                rows["value"] = rows["value"].split(" ")
        else:
            rows["value"] = [rows["value"]]

        return rows

    def _get_measurement_methods(self, measurement_methods, measure_name, entity_name):
        measurement_methods = measurement_methods[
            (measurement_methods.measure == measure_name) & (measurement_methods.data_type == entity_name)
        ]
        measurement_methods = measurement_methods.apply(self._measurement_methods_reformatting, axis=1).set_index(
            "column_name"
        )

        return measurement_methods

    @classmethod
    def _fill(cls, rows, data):
        rows.value.extend(["", "-1", " ", None, "none"])
        data[rows.name] = [str(x).replace(".0", "") for x in data[rows.name]]
        fill = ~(data[rows.name].isin(rows.value)) & ~(data[rows.name].isna())

        return fill

    def _completeness_reformatting(self, rows, entity):
        if rows.condition_indicator:
            if rows.condition_is_not:
                column_measure = entity[~entity[rows.condition_column].isin(rows.condition_value)][
                    ["medical_education_number"]
                ].copy()
            else:
                column_measure = entity[entity[rows.condition_column].isin(rows.condition_value)][
                    ["medical_education_number"]
                ].copy()
        else:
            column_measure = entity[["medical_education_number"]].copy()
        if not column_measure.empty:
            measured = self._fill(rows, entity)
            column_measure["element"] = rows.name
            column_measure["measure"] = rows.measure
            column_measure["value"] = measured
            column_measure["raw_value"] = list(entity[rows.name].loc[column_measure.index])
            self._measure = pandas.concat([self._measure, column_measure])

    def _measure_completeness(self, measurement_methods, entity):
        measurement_methods.apply(self._completeness_reformatting, args=(entity,), axis=1)

        return self._measure
