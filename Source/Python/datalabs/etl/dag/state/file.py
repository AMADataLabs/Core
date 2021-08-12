""" File-based DAG state classes. """
from   dataclasses import dataclass
from   datetime import datetime
import os
from   pathlib import Path

from   dateutil.parser.isoparser import isoparse
import pytz

from   datalabs.etl.dag.state.base import State, Status
from   datalabs.parameter import add_schema


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGStateParameters:
    base_path: str
    unknowns: dict=None


class DAGState(State):
    PARAMETER_CLASS = DAGStateParameters

    def connect(self):
        pass

    def close(self):
        pass

    def get_dag_status(self, dag: str, execution_time: str):
        return self._get_status(dag, "", execution_time)

    def get_task_status(self, dag: str, task: str, execution_time: str):
        return self._get_status(dag, task, execution_time)

    def set_dag_status(self, dag: str, execution_time: str, status: Status):
        self._set_status(dag, "", execution_time, status)

    def set_task_status(self, dag: str, task: str, execution_time: str, status: Status):
        self._set_status(dag, task, execution_time, status)

    def _get_status(self, dag: str, task: str, execution_time: str):
        state_path = self._generate_state_path(dag, task, execution_time)
        status = Status.UNKNOWN

        try:
            with open(state_path) as file:
                status = Status(file.read())
        except FileNotFoundError:
            pass

        return status

    def _set_status(self, dag: str, task: str, execution_time: datetime, status: Status):
        state_path = self._generate_state_path(dag, task, execution_time)

        if not state_path.parent.exists():
            os.makedirs(state_path.parent)

        with open(state_path, 'w') as file:
            file.write(status.value)

    def _generate_state_path(self, dag: str, task: str, execution_time: str):
        execution_time = isoparse(execution_time).astimezone(pytz.timezone("UTC"))
        datestamp = execution_time.strftime('%Y-%m-%d')
        timestamp = execution_time.strftime('%H%M%S')

        return Path(self._parameters.base_path, dag, task, datestamp, f'state_{timestamp}')
