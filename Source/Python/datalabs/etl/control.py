""" DAG execution from a task. """
from   dataclasses import dataclass
from   datetime import datetime
from   io import BytesIO
import json
import logging

import pandas

from datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DAGNotificationFactoryParameters:
    dag: str
    execution_time: str
    data: object


class DAGNotificationFactoryTask(TransformerTask):
    PARAMETER_CLASS = DAGNotificationFactoryParameters

    def _transform(self):
        iteration_parameters = self._parse_iteration_parameters(self._parameters.data)

        return [
            json.dumps(self._generate_notification_messages(
                self._parameters.dag,
                self._parameters.execution_time,
                iteration_parameters
            )).encode()
        ]

    @classmethod
    def _parse_iteration_parameters(cls, data):
        csv_data = (pandas.read_csv(BytesIO(file), dtype=object) for file in data)

        return pandas.concat(csv_data, ignore_index=True)

    @classmethod
    def _generate_notification_messages(cls, dag, execution_time, parameters):
        parameters["dag"] = dag
        parameters["execution_time"] = execution_time

        parameters.dag = parameters.dag + ":" + parameters.index.astype(str)

        return list(parameters.apply(cls._generate_notification_message, axis="columns"))

    @classmethod
    def _generate_notification_message(cls, parameters):
        dag = parameters.dag
        execution_time = parameters.execution_time

        return dict(
            dag=dag,
            execution_time=execution_time,
            parameters=json.loads(parameters.drop(["dag", "execution_time"]).to_json())
        )
