""" Convert a DAG schedule into a list of DAGs to run. """
from   dataclasses import dataclass
from   datetime import datetime, timedelta
from   functools import partial
from   io import BytesIO
from   itertools import takewhile, chain
import json
import logging

from   dateutil.parser import isoparse
from   croniter import croniter
import pandas

from   datalabs.etl.dag.state import Status, StatefulDAGMixin
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGSchedulerParameters:
    interval_minutes: str
    dag_state: str
    execution_time: str


class DAGSchedulerTask(ExecutionTimeMixin, StatefulDAGMixin, Task):
    PARAMETER_CLASS = DAGSchedulerParameters

    def run(self):
        schedule = None

        try:
            schedule = pandas.read_csv(BytesIO(self._data[0]))
            LOGGER.info("Schedule:\n%s", schedule)
        except Exception as exception:
            raise ValueError(f'Bad schedule data: {self._data[0]}') from exception

        dags = self._determine_dags_to_run(schedule, self._get_target_execution_time())
        LOGGER.info("Dags to Run:\n%s", dags)

        return [json.dumps(self._generate_notification_messages(dags)).encode()]

    # pylint: disable=no-self-use
    def _get_target_execution_time(self):
        return isoparse(self._parameters.execution_time)

    def _determine_dags_to_run(self, schedule, target_execution_time):
        scheduled_dags = pandas.DataFrame(columns=["dag", "execution_time"])

        if len(schedule) > 0:
            base_time = target_execution_time - timedelta(minutes=int(self._parameters.interval_minutes))
            LOGGER.debug('Base time: %s', base_time)
            schedule["execution_time"] = self._get_execution_times(schedule, base_time)
            schedule["scheduled"] = self._get_scheduled_dags(schedule, base_time)
            schedule["started"] = self._get_started_dags(schedule)
            LOGGER.debug('Schedule: %s', schedule)

            scheduled_dags = schedule[schedule.scheduled & ~schedule.started][["dag", "execution_time"]]

        return scheduled_dags

    @classmethod
    def _generate_notification_messages(cls, dags):
        message_data = dags[["dag", "execution_time"]]
        message_data.execution_time = message_data.execution_time.apply(lambda d: d.isoformat())
        return [json.loads(row[1].to_json()) for row in message_data.iterrows()]

    def _get_execution_times(self, schedule, base_time):
        return schedule.apply(partial(self._get_execution_time, base_time), axis = 1)

    def _get_scheduled_dags(self, schedule, base_time):
        execution_times = schedule.execution_time
        execution_time_bounds = self._get_execution_time_bounds(base_time)

        return (execution_times >= execution_time_bounds[0]) & (execution_times < execution_time_bounds[1])

    def _get_started_dags(self, schedule):
        state = self._get_state_plugin(self._parameters)

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

        status = state.get_dag_status(dag["dag"], dag["execution_time"].to_pydatetime().isoformat())

        return status != Status.UNKNOWN

# pylint: disable=line-too-long
class ScheduledDAGIdentifierTask(DAGSchedulerTask):
    PARAMETER_CLASS = DAGSchedulerParameters

    # pylint: disable=too-many-locals
    def _determine_dags_to_run(self, schedule, target_execution_time):
        scheduled_dags = pandas.DataFrame(columns=["dag", "execution_time"])

        scheduled_dags = self._get_last_days_runs(schedule, target_execution_time)

        scheduled_dags = scheduled_dags.rename(columns={"run": "execution_time"}).reset_index()

        return scheduled_dags

    # pylint: disable=unsupported-assignment-operation, no-member
    @classmethod
    def _get_last_days_runs(cls, schedule, now=None):
        now = datetime.utcnow() if now is None else now
        base_time = now - timedelta(hours=24)

        dag_runs = schedule.schedule.apply(lambda cron_descriptor: croniter(cron_descriptor, base_time))

        schedule["run"] = dag_runs.apply(lambda x: list(chain(*cls._get_dag_runs(x, now))))

        schedule.drop(columns="schedule", inplace=True)

        return schedule.explode("run")

    @classmethod
    def _get_dag_runs(cls, dag_runs, now):
        yield list(takewhile(lambda p: p < now, dag_runs.all_next(datetime)))
