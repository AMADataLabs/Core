""" Convert a DAG schedule into a list of DAGs to run. """
from   dataclasses import dataclass
from   datetime import datetime, timedelta
from   functools import partial
from   io import BytesIO
import json
import logging
from   typing import Iterator

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

        target_execution_time_at_previous_day = target_execution_time  - timedelta(days=1)

        if ~(schedule["schedule"].str.contains("/", na=False).any()):
            scheduled_dags = super()._determine_dags_to_run(schedule, target_execution_time_at_previous_day)
        else:
            if len(schedule) > 0:
                dags_with_repeat_schedule, dags_without_repeat_schedule = self._split_dags(schedule)

                without_repeat_schedule = super()._determine_dags_to_run(dags_without_repeat_schedule, target_execution_time_at_previous_day)

                start = target_execution_time_at_previous_day
                stop = target_execution_time
                schedule_list = []

                for _, row in dags_with_repeat_schedule.iterrows():
                    dag_name = row.dag

                    schedules = list(self._next_all_valid_schedules(row.schedule, start, stop))

                    schedule_list.append((dag_name, schedules))

                repeat_schedule_list = [(i, k) for i, j in schedule_list for k in j]
                repeat_schedule = pandas.DataFrame(repeat_schedule_list, columns = ["dag", "execution_time"])

                scheduled_dags = pandas.concat([without_repeat_schedule, repeat_schedule], ignore_index=True, axis=0)

        return scheduled_dags

    @classmethod
    def _next_all_valid_schedules(cls, schedule: str, start: datetime, stop: datetime) -> Iterator[datetime]:
        crons = croniter(schedule, start - timedelta(seconds=1))
        previous = start - timedelta(days=1)

        for eta in crons.all_next(datetime):
            if eta >= stop:
                break
            if eta < start:
                continue
            if eta - previous < timedelta(0):
                continue

            yield eta
            previous = eta

    @classmethod
    def _split_dags(cls, schedule):
        dags_with_repeat_schedule = schedule[(schedule["schedule"].str.contains("/", na=False))]
        dags_without_repeat_schedule = schedule[~(schedule["schedule"].str.contains("/", na=False))]

        return dags_with_repeat_schedule, dags_without_repeat_schedule
