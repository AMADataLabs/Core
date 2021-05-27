""" Convert a DAG schedule into a list of DAGs to run. """
from   abc import ABC, abstractmethod
from   dataclasses import dataclass
from   datetime import datetime, timedelta
from   functools import partial
from   io import BytesIO

import botocore.exceptions
from   croniter import croniter
import csv
import logging
import pandas

import datalabs.etl.task as task
import datalabs.etl.transform as transform
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGSchedulerParameters:
    interval_minutes: str
    state_class: str
    unknowns: dict = None
    data: object = None


class DAGScheduler(task.ExecutionTimeMixin, transform.TransformerTask):
    PARAMETER_CLASS = DAGSchedulerParameters

    def _transform(self):
        LOGGER.info(self._parameters.data)
        schedule = None

        try:
            schedule = pandas.read_csv(BytesIO(self._parameters.data[0]))
        except Exception as exception:
            raise ValueError('Bad schedule data: %s', self._parameters.data[0]) from exception

        dag_names = self._determine_dags_to_run(schedule)

        return [data.encode('utf-8', errors='backslashreplace') for data in dag_names]

    def _determine_dags_to_run(self, schedule):
        now = datetime.utcnow()

        schedule["execution_time"] = self._get_execution_times(schedule, now)
        schedule["scheduled"] = self._get_scheduled_dags(schedule, now)
        schedule["started"] = self._get_started_dags(schedule)

        return schedule.name[schedule.started & ~schedule.started]

    def _get_execution_times(self, schedule, now):
        base_time = now - timedelta(minutes=int(self._parameters.interval_minutes))

        return schedule.apply(partial(self._get_execution_time, base_time), axis = 1)

    def _get_scheduled_dags(self, schedule, now):
        execution_time_bounds = self._get_execution_time_bounds(now)
        
        return schedule.execution_time >= execution_time_bounds[0] & schedule.execution_time < execution_time_bounds[1]

    def _get_started_dags(self, schedule):
        state = self._get_state_plugin()

        return schedule.apply(lambda dag: self._is_started(state, dag), axis = 1)

    def _get_execution_time_bounds(self, base_time):
        execution_times = croniter(f'*/{self._parameters.interval_minutes} * * * *', base_time)

        return (execution_times.get_next(datetime), execution_times.get_next(datetime))

    def _get_execution_time(self, base_time, dag):
        return croniter(dag["schedule"], base_time).get_next(datetime)

    def _is_started(self, state, dag):
        import pdb; pdb.set_trace()
        status = state.get_status(dag["name"], dag["execution_time"])

        return status == 'Pending' or status == 'Started'

    def _get_state_plugin(self):
        parameters = self._parameters.unknowns
        state_plugin = import_plugin(self._parameters.state_class)
        state_parameter_keys = list(state_plugin.PARAMETER_CLASS.SCHEMA.fields.keys())
        state_parameters = {key:value for key, value in parameters.items() if key in state_parameter_keys}

        return state_plugin(state_parameters)
