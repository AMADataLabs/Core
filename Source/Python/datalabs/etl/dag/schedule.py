""" Convert a DAG schedule into a list of DAGs to run. """
from   abc import ABC, abstractmethod
from   dataclasses import dataclass
from   io import BytesIO

import botocore.exceptions
import csv
import logging
import pandas
import schedule

import datalabs.etl.transform as etl
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGSchedulerParameters:
    state_class: str
    unknowns: dict = None
    data: object = None


class DAGScheduler(etl.ExecutionTimeMixin, etl.TransformerTask):
    PARAMETER_CLASS = DAGSchedulerParameters

    def _transform(self):
        LOGGER.info(self._parameters['data'])
        schedule = None

        try:
            schedule = pandas.read_csv(BytesIO(self._parameters['data'][0]))
        except Exception as exception:
            raise ValueError('Bad schedule data: %s', self._parameters['data']) from exception

        dag_names = self._determine_dags_to_run(schedule)

        return [data.encode('utf-8', errors='backslashreplace') for data in dag_names]

    def _determine_dags_to_run(self, schedule):
        state = self._get_state_plugin()

        schedule["execution_time"] = schedule.apply(self._get_execution_time)

        schedule["started"] = schedule.apply(lambda dag: self._is_started(state, dag))

        return schedule.name[schedule.started == False]

    def _get_execution_time(self, dag):
        pass

    def _is_started(self, state, dag):
        state = state.get_status(dag['name'], dag['execution_time'])

        return state["status"] == 'Pending' or state["status"] == 'Started'

    def _get_state_plugin(self):
        parameters = self._parameters.unknowns
        state_plugin = import_plugin(self._parameters.state_class)
        state_parameter_keys = list(state_plugin.PARAMETER_CLASS.SCHEMA.fields.keys())
        state_parameters = {key:value for key, value in parameters.items() if key in state_parameter_keys}

        return state_plugin(state_parameters)
