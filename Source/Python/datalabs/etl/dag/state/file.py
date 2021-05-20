""" File-based DAG state classes. """
from   dataclasses import dataclass
from   datetime import datetime
import os
from   pathlib import Path

import pytz

from   datalabs.etl.dag.state.base import State, Status
from   datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGStateParameters:
    base_path: str


class DAGState(State):
    PARAMETER_CLASS = DAGStateParameters

    def connect(self):
        pass

    def get_status(self, name: str, execution_time: datetime):
        state_path = self._generate_state_path(name, execution_time)
        status = Status.Unknown

        try:
            with open(state_path) as file:
                status = Status(file.read())
        except FileNotFoundError:
            pass

        return status

    def set_status(self, name: str, execution_time: datetime, status: Status):
        state_path = self._generate_state_path(name, execution_time)

        if not state_path.parent.exists():
            os.makedirs(state_path.parent)

        with open(state_path, 'w') as file:
            file.write(status.value)

    def _generate_state_path(self, name: str, execution_time: datetime):
        execution_time = execution_time.astimezone(pytz.timezone("UTC"))
        datestamp = execution_time.strftime('%Y-%m-%d')
        timestamp = execution_time.strftime('%H%M%S')

        return Path(self._parameters.base_path, name, datestamp, f'state_{timestamp}')
