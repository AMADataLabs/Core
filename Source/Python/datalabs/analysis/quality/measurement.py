""" Measurement for various metrics """
from datetime import datetime
import logging
import re

import pandas
from numpy import nan

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MeasurementMethods:
    def __init__(self, measurement_methods) -> None:
        self._entity_measurement = pandas.DataFrame()
        self._measurement_methods = measurement_methods

    @classmethod
    def create_measurement_methods(cls, measurement_methods, measure_name, entity_name):
        measurement_methods = measurement_methods[
            (measurement_methods.measure == measure_name) & (measurement_methods.data_type == entity_name)
        ]

        measurement_methods = measurement_methods.apply(cls._reformat_rule, axis=1).set_index("column_name")

        return MeasurementMethods(measurement_methods)

    @classmethod
    def _reformat_rule(cls, rule):
        rule["condition_value"] = cls._reformat_values(rule["condition_value"])

        rule["value"] = cls._reformat_values(rule["value"])

        return rule

    @classmethod
    def _reformat_values(cls, values):
        if isinstance(values, str):
            values = values.strip()
            if " " in values:
                values = values.split(" ")
            elif re.compile(r"\d{1,2}/\d{1,2}/\d{4}").match(values):
                values = [datetime.strptime(values, "%m/%d/%Y").strftime("%Y-%m-%d")]
            else:
                values = [values]
        else:
            values = [values]

        return values

    @classmethod
    def _are_values_filled(cls, rules, data):
        rules.value.extend(["", "-1", " ", None, "none", "nan", nan])

        return ~(data[rules.name].isin(rules.value))

    def _apply_completeness_rule(self, rule, entities):
        if rule.condition_indicator:
            entities = self._select_condition_matching_entities(rule, entities)

        column_completeness = self._generate_column_completeness(rule, entities)

        if not column_completeness.empty:
            self._entity_measurement = pandas.concat([self._entity_measurement, column_completeness])

    @classmethod
    def _generate_column_completeness(cls, rule, entities):
        column_completeness = entities[["medical_education_number"]].copy()

        if not column_completeness.empty:
            measured = cls._are_values_filled(rule, entities)
            column_completeness["element"] = rule.name
            column_completeness["measure"] = rule.measure
            column_completeness["value"] = measured
            column_completeness["raw_value"] = list(entities[rule.name].loc[column_completeness.index])

        return column_completeness

    @classmethod
    def _select_condition_matching_entities(cls, rule, entities):
        if rule.condition_is_not:
            entities = entities[~entities[rule.condition_column].isin(rule.condition_value)]
        else:
            entities = entities[entities[rule.condition_column].isin(rule.condition_value)]

        return entities

    def _filter_measurement_methods(self, entity):
        return self._measurement_methods[self._measurement_methods.index.isin(entity.columns.tolist())]

    def measure_completeness(self, entity):
        self._measurement_methods = self._filter_measurement_methods(entity)

        self._measurement_methods.apply(self._apply_completeness_rule, args=(entity,), axis=1)

        return self._entity_measurement
