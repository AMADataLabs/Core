""" Convert a DAG schedule into a list of DAGs to run. """
from   dataclasses import dataclass
from   datetime import datetime, timedelta
from   functools import partial
from   io import BytesIO
import logging
import pickle

from   dateutil.parser import isoparse
from   croniter import croniter
import pandas

from   datalabs.etl.dag.state import Status
from   datalabs.etl.task import ExecutionTimeMixin
import datalabs.etl.transform as transform
from   datalabs.parameter import add_schema
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGSchedulerParameters:
    interval_minutes: str
    dag_state_class: str
    execution_time: str
    data: object = None
    unknowns: dict = None


class DAGSchedulerTask(ExecutionTimeMixin, transform.TransformerTask):
    PARAMETER_CLASS = DAGSchedulerParameters

    def _transform(self):
        schedule = None

        try:
            schedule = pandas.read_csv(BytesIO(self._parameters.data[0]))
            LOGGER.info("Schedule:\n%s", schedule)
        except Exception as exception:
            raise ValueError(f'Bad schedule data: {self._parameters.data[0]}') from exception

        dags = self._determine_dags_to_run(schedule, self._get_target_execution_time())
        LOGGER.info("Dags to Run:\n%s", dags)

        return [self._generate_notification_messages(dags)]

    # pylint: disable=no-self-use
    def _get_target_execution_time(self):
        return isoparse(self._parameters.execution_time)

    def _determine_dags_to_run(self, schedule, target_execution_time):
        base_time = target_execution_time - timedelta(minutes=int(self._parameters.interval_minutes))
        LOGGER.debug('Base time: %s', base_time)
        schedule["execution_time"] = self._get_execution_times(schedule, base_time)
        schedule["scheduled"] = self._get_scheduled_dags(schedule, base_time)
        schedule["started"] = self._get_started_dags(schedule)
        LOGGER.debug('Schedule: %s', schedule)

        return schedule[schedule.scheduled & ~schedule.started]

    @classmethod
    def _generate_notification_messages(cls, dags):
        message_data = dags[["name", "execution_time"]].rename(columns=dict(name="dag"))
        messages = [row[1].to_json() for row in message_data.iterrows()]

        return pickle.dumps(messages)

    def _get_execution_times(self, schedule, base_time):
        return schedule.apply(partial(self._get_execution_time, base_time), axis = 1)

    def _get_scheduled_dags(self, schedule, base_time):
        execution_times = schedule.execution_time
        execution_time_bounds = self._get_execution_time_bounds(base_time)

        return (execution_times >= execution_time_bounds[0]) & (execution_times < execution_time_bounds[1])

    def _get_started_dags(self, schedule):
        state = self._get_state_plugin()

        return schedule.apply(lambda dag: self._is_started(state, dag), axis = 1)

    def _get_execution_time_bounds(self, base_time):
        execution_times = croniter(f'*/{self._parameters.interval_minutes} * * * *', base_time)

        return (execution_times.get_next(datetime), execution_times.get_next(datetime))

    @classmethod
    def _get_execution_time(cls, base_time, dag):
        return croniter(dag["schedule"], base_time).get_next(datetime)

    @classmethod
    def _is_started(cls, state, dag):
        status = None

        status = state.get_dag_status(dag["name"], dag["execution_time"].to_pydatetime().isoformat())

        return status != Status.UNKNOWN

    def _get_state_plugin(self):
        parameters = self._parameters.unknowns
        state_plugin = import_plugin(self._parameters.dag_state_class)
        state_parameter_keys = list(state_plugin.PARAMETER_CLASS.SCHEMA.fields.keys())
        state_parameters = {key:value for key, value in parameters.items() if key in state_parameter_keys}

        return state_plugin(state_parameters)
